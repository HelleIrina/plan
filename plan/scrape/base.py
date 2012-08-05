# This file is part of the plan timetable generator, see LICENSE for details.

import logging

from plan.common.models import Course, Semester


class Scraper(object):
    def __init__(self, semester, options):
        self.semester = semester
        self.options = options
        self.stats = {'created': 0,
                      'updated': 0,
                      'deleted': 0}

    def delete(self, items):
        raise NotImplementedError

    def fetch(self, match=None):
        raise NotImplementedError

    def run(self):
        return self.fetch()

    def needs_commit(self):
        return True

    def clean(self, raw_text):
        text = raw_text.strip()
        if text[0] in ('"', "'") and text[0] == text[-1]:
            text = text[1:-1].strip()
        return text


class CourseScraper(Scraper):
    FIELDS = ('code', 'version')
    CLEAN_FIELDS = ('name',)
    DEFAULT_FIELDS = ('name', 'url', 'points')

    def delete(self, courses):
        course_ids = [c.id for c in courses]
        Course.objects.filter(id__in=course_ids).delete()

    def needs_commit(self):
        return (self.stats['created'] > 0 or
                self.stats['updated'] > 0 or
                self.stats['deleted'] > 0)

    def run(self):
        semester, created = Semester.objects.get_or_create(
            year=self.semester.year, type=self.semester.type)
        to_delete = []

        for data in self.fetch():
            # Build kwargs for get or create by:
            #  1. cleaning fields that are in CLEAN_FIELDS
            #  2. adding lookup fields that are in FIELDS
            #  3. adding defaults fields that are in DEFAULT_FIELDS
            kwargs = {'defaults': {}, 'semester': semester}
            for field in data:
                if field in self.CLEAN_FIELDS:
                    data[field] = self.clean(data[field])

                if field in self.FIELDS:
                    kwargs[field] = data[field]
                elif field in self.DEFAULT_FIELDS:
                    kwargs['defaults'][field] = data[field]

            if data.get('delete', False):
                try:
                    del kwargs['defaults']
                    to_delete.append(Course.objects.get(**kwargs))
                    self.stats['deleted'] += 1
                except Course.DoesNotExist:
                    pass
                continue

            course, created = Course.objects.get_or_create(**kwargs)
            changes = {}

            if created:
                self.stats['created'] += 1
            else:
                # Check if any of the non lookup fields need to be fixed.
                for field, value in kwargs['defaults'].items():
                    old_value = getattr(course, field)
                    if old_value != value:
                        setattr(course, field, value)
                        changes[field] = (old_value, value)

            # TODO(adamcik): use update_fields once we have django 1.5
            if changes:
                course.save()
                self.stats['updated'] += 1

            if created:
                logging.info('Added course %s', course.code)
            elif changes:
                logging.info('Updated course %s:', course.code)
                for key, (new, old) in changes.items():
                    if (isinstance(old, basestring) and
                        isinstance(new, basestring) and
                        new.strip() == old.strip()):
                        logging.info('  %s: <whitespace fix>', key)
                    else:
                        logging.info('  %s: [%s] -> [%s]', key, new, old)
            else:
                logging.debug('No changes for course %s', course.code)

        return to_delete
