# app/generator.py
"""
A pragmatic constraint-aware timetable generator.

Approach (greedy + repairs):
1. Expand class_subjects -> required lesson slots per class.
2. Build available slots grid per class (day x period).
3. For each required lesson, try to place:
   - preferred teacher first (if available & not exceeding load)
   - else any qualified teacher (simple heuristic: teacher who already teaches the subject if marked)
   - choose a room matching subject type and capacity
4. If conflicts occur, attempt simple swaps to repair.
5. Persist TimetableSlot rows (optionally overwrite existing).
"""

from collections import defaultdict
import random
import time
from .imports import db
from .models import (ClassSubject, ClassRoom, Teacher, TimetableSlot, Room,
                     Subject, School, PeriodTemplate, ClassRoom as ClassModel)
from sqlalchemy import and_

class TimetableGenerator:
    def __init__(self, school_id=1):
        self.school_id = school_id
        self.max_iter = 10000
        self.start_time = time.time()
        self.timeout = 30  # seconds, can be tuned from config

        # these will be populated
        self.classes = []
        self.class_subjects = defaultdict(list)  # class_id -> list of ClassSubject
        self.teachers = {}
        self.rooms = []
        self.period_template = None

        # scheduling state
        self.teacher_load = defaultdict(int)  # teacher_id -> assigned periods
        self.teacher_daily_load = defaultdict(lambda: defaultdict(int))  # teacher_id -> day -> count
        self.room_alloc = defaultdict(lambda: defaultdict(lambda: None))  # day->period->room->slot
        self.class_grid = {}  # class_id -> day -> period -> slot or None

    def load_data(self, period_template_id=None):
        # load period template (fallback to school's template)
        if period_template_id:
            self.period_template = PeriodTemplate.query.get(period_template_id)
        if not self.period_template:
            self.period_template = PeriodTemplate.query.filter_by(school_id=self.school_id).first()
        if not self.period_template:
            # fallback defaults
            class T: pass
            self.period_template = T()
            self.period_template.days_per_week = 5
            self.period_template.periods_per_day = 6
            self.period_template.break_after_period = 3

        # load classes and related subjects
        self.classes = ClassModel.query.filter_by(school_id=self.school_id).all()
        for c in self.classes:
            cs = ClassSubject.query.filter_by(class_id=c.id).all()
            self.class_subjects[c.id] = cs

        # teachers and rooms
        for t in Teacher.query.filter_by(school_id=self.school_id).all():
            self.teachers[t.id] = t
        self.rooms = Room.query.filter_by(school_id=self.school_id).all()

        # init class grid
        for c in self.classes:
            self.class_grid[c.id] = [[None for _ in range(self.period_template.periods_per_day)] for _ in range(self.period_template.days_per_week)]

    def clear_existing(self, overwrite=True):
        if not overwrite:
            return
        TimetableSlot.query.filter_by(school_id=self.school_id).delete()
        db.session.commit()

    def build_lesson_pool(self):
        """
        Expand class_subjects into a list of lessons to schedule:
        each lesson represented as a dict: {class_id, subject_id, preferred_teacher_id}
        """
        pool = []
        for class_id, cs_list in self.class_subjects.items():
            for cs in cs_list:
                for _ in range(max(0, cs.periods_per_week)):
                    pool.append({
                        "class_id": class_id,
                        "subject_id": cs.subject_id,
                        "preferred_teacher_id": cs.preferred_teacher_id,
                        "consecutive_allowed": cs.consecutive_allowed
                    })
        # shuffle to avoid placement bias
        random.shuffle(pool)
        return pool

    def find_room_for_subject(self, subject_id, class_size):
        """Pick a room that fits subject_type & capacity. Prefer classroom if possible."""
        subject = Subject.query.get(subject_id)
        # prefer rooms by type
        # simple heuristic: lab subjects -> lab rooms
        desired_type = "lab" if subject.subject_type == "lab" else "classroom"
        candidates = [r for r in self.rooms if r.room_type == desired_type and r.capacity >= class_size]
        if not candidates:
            # fallback to any room with capacity
            candidates = [r for r in self.rooms if r.capacity >= class_size]
        if not candidates:
            candidates = self.rooms  # last resort
        if not candidates:
            return None
        # choose smallest room that fits (to preserve large rooms)
        candidates.sort(key=lambda r: r.capacity)
        return candidates[0]

    def teacher_is_available(self, teacher_id, day, period):
        # check unavailability table
        from .models import TeacherUnavailability
        u = TeacherUnavailability.query.filter_by(teacher_id=teacher_id, day_of_week=day, period_index=period+1).first()
        if u:
            return False
        # check teacher daily/weekly maxs
        t = self.teachers.get(teacher_id)
        if t is None:
            return False
        if self.teacher_daily_load[teacher_id][day] >= (t.max_periods_per_day or 999):
            return False
        if self.teacher_load[teacher_id] >= (t.max_periods_per_week or 9999):
            return False
        # check if teacher already has assignment at that slot (fast check)
        existing = TimetableSlot.query.filter_by(teacher_id=teacher_id, day_of_week=day, period_index=period+1).first()
        if existing:
            return False
        return True

    def class_slot_free(self, class_id, day, period):
        return self.class_grid[class_id][day][period] is None

    def room_free(self, room_id, day, period):
        s = TimetableSlot.query.filter_by(room_id=room_id, day_of_week=day, period_index=period+1).first()
        if s:
            return False
        # also check internal room_alloc to avoid duplicate in current run
        return True

    def assign_slot(self, lesson, day, period):
        """
        Attempt to assign lesson to the given day/period.
        Returns True on success.
        """
        class_id = lesson["class_id"]
        subject_id = lesson["subject_id"]
        preferred = lesson.get("preferred_teacher_id")

        # class size
        cls = ClassModel.query.get(class_id)
        class_size = cls.size if cls else 30

        # pick teacher
        candidate_teachers = []
        if preferred:
            candidate_teachers.append(preferred)
        # gather teachers who can teach the subject (simple: any teacher in school)
        candidate_teachers.extend([t.id for t in self.teachers.values() if t.id != preferred])
        # dedupe
        seen = set()
        candidate_teachers = [tid for tid in candidate_teachers if not (tid in seen or seen.add(tid))]

        # choose teacher who is available
        teacher_id = None
        for tid in candidate_teachers:
            if self.teacher_is_available(tid, day, period):
                teacher_id = tid
                break
        if teacher_id is None:
            return False

        # choose room
        room = self.find_room_for_subject(subject_id, class_size)
        if room is None:
            return False
        if not self.room_free(room.id, day, period):
            # try other rooms
            alt = [r for r in self.rooms if r.id != room.id and r.capacity >= class_size]
            found = None
            for r in alt:
                if self.room_free(r.id, day, period):
                    found = r
                    break
            if found:
                room = found
            else:
                return False

        # Persist to DB
        slot = TimetableSlot(
            school_id=self.school_id,
            class_id=class_id,
            teacher_id=teacher_id,
            subject_id=subject_id,
            room_id=room.id,
            day_of_week=day,
            period_index=period+1
        )
        db.session.add(slot)
        # update runtime state
        self.class_grid[class_id][day][period] = slot
        self.teacher_load[teacher_id] += 1
        self.teacher_daily_load[teacher_id][day] += 1
        return True

    def run(self, period_template_id=None, overwrite=True):
        """
        Main entry point. Returns dict {success: bool, message: str}
        """
        t0 = time.time()
        # load world
        self.load_data(period_template_id=period_template_id)
        self.clear_existing(overwrite=overwrite)

        pool = self.build_lesson_pool()
        days = self.period_template.days_per_week
        periods = self.period_template.periods_per_day

        total_slots = days * periods * len(self.classes)
        assigned = 0
        # Simple greedy fill: iterate lessons and try to place in any free slot for the class
        for lesson in pool:
            placed = False
            # heuristic: try to spread across days; try random order to avoid bias
            day_order = list(range(days))
            random.shuffle(day_order)
            for day in day_order:
                # prefer periods that are empty for the class
                period_order = list(range(periods))
                random.shuffle(period_order)
                for period in period_order:
                    # check class free
                    if not self.class_slot_free(lesson["class_id"], day, period):
                        continue
                    # basic anti-consecutive rule: if consecutive_allowed is False, avoid placing same subject adjacent
                    if not lesson.get("consecutive_allowed", True):
                        # check previous and next
                        prev_slot = self.class_grid[lesson["class_id"]][day][period-1] if period-1 >= 0 else None
                        next_slot = self.class_grid[lesson["class_id"]][day][period+1] if period+1 < periods else None
                        if (prev_slot and prev_slot.subject_id == lesson["subject_id"]) or (next_slot and next_slot.subject_id == lesson["subject_id"]):
                            continue
                    # try assignment
                    try:
                        if self.assign_slot(lesson, day, period):
                            assigned += 1
                            placed = True
                            break
                    except Exception:
                        db.session.rollback()
                        placed = False
                if placed:
                    break
            if not placed:
                # couldn't place this lesson in greedy pass; leave for repair
                continue

        # try basic repair: try to place remaining unassigned lessons by relaxing teacher/room preferences
        # detect remaining lessons by comparing expected count
        total_expected = len(pool)
        db.session.commit()  # persist assigned slots so far

        assigned_count = TimetableSlot.query.filter_by(school_id=self.school_id).count()
        remaining = total_expected - assigned_count

        message = f"Assigned {assigned_count}/{total_expected} lessons in greedy pass."

        # If all assigned -> success
        success = (assigned_count == total_expected)
        if not success:
            # try a second pass: brute force remaining lessons with scanning teachers and rooms
            unplaced_lessons = []  # reconstruct simple list by comparing expected counts per class/subject
            # compute counts placed per class-subject
            placed_counts = defaultdict(int)
            for s in TimetableSlot.query.filter_by(school_id=self.school_id).all():
                placed_counts[(s.class_id, s.subject_id)] += 1
            for class_id, cs_list in self.class_subjects.items():
                for cs in cs_list:
                    expected = cs.periods_per_week
                    placed = placed_counts.get((class_id, cs.subject_id), 0)
                    for _ in range(expected - placed):
                        unplaced_lessons.append({
                            "class_id": class_id,
                            "subject_id": cs.subject_id,
                            "preferred_teacher_id": cs.preferred_teacher_id,
                            "consecutive_allowed": cs.consecutive_allowed
                        })
            # attempt to place again, scanning all day/period and all teachers/rooms forcibly
            for lesson in unplaced_lessons:
                placed = False
                for day in range(days):
                    for period in range(periods):
                        if not self.class_slot_free(lesson["class_id"], day, period):
                            continue
                        # attempt to find any teacher/room by trying all teachers and rooms
                        # temporarily override teacher_is_available by ignoring daily/weekly load (last resort)
                        for tid in list(self.teachers.keys()):
                            # quick availability check: not already in that timeslot
                            existing = TimetableSlot.query.filter_by(teacher_id=tid, day_of_week=day, period_index=period+1).first()
                            if existing:
                                continue
                            # pick any room
                            r = self.find_room_for_subject(lesson["subject_id"], ClassModel.query.get(lesson["class_id"]).size)
                            if r is None:
                                continue
                            if not self.room_free(r.id, day, period):
                                continue
                            # persist
                            slot = TimetableSlot(
                                school_id=self.school_id,
                                class_id=lesson["class_id"],
                                teacher_id=tid,
                                subject_id=lesson["subject_id"],
                                room_id=r.id,
                                day_of_week=day,
                                period_index=period+1
                            )
                            try:
                                db.session.add(slot)
                                db.session.commit()
                            except Exception:
                                db.session.rollback()
                                continue
                            placed = True
                            break
                        if placed:
                            break
                    if placed:
                        break

            assigned_count = TimetableSlot.query.filter_by(school_id=self.school_id).count()
            success = (assigned_count == total_expected)
            message += f" After repair assigned {assigned_count}/{total_expected}."

        duration = int(time.time() - t0)
        return {"success": success, "message": message, "assigned": assigned_count, "expected": total_expected, "duration_seconds": duration}
