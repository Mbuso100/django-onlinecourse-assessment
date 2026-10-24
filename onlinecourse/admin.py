from django.contrib import admin
from .models import Course, Lesson, Instructor, Learner, Question, Choice, Submission
class ChoiceInline(admin.StackedInline):
    model=Choice
    extra=4
class QuestionInline(admin.StackedInline):
    model=Question
    extra=1
class LessonInline(admin.StackedInline):
    model=Lesson
    extra=5
@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    inlines=[LessonInline,QuestionInline]
    list_display=['name','pub_date']
@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    inlines=[ChoiceInline]
    list_display=['question_text','course','grade']
admin.site.register(Lesson)
admin.site.register(Instructor)
admin.site.register(Learner)
admin.site.register(Choice)
admin.site.register(Submission)
