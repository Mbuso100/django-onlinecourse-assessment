from pathlib import Path
p=Path(__file__).resolve().parent
a=p/'onlinecourse'
m=a/'models.py'
s=m.read_text()
if 'class Question(models.Model):' not in s:
 m.write_text(s+"""
class Question(models.Model):
    course = models.ForeignKey(Course,on_delete=models.CASCADE)
    question_text = models.CharField(max_length=200)
    grade = models.IntegerField(default=1)
    def __str__(self): return self.question_text

class Choice(models.Model):
    question = models.ForeignKey(Question,on_delete=models.CASCADE)
    choice_text = models.CharField(max_length=200)
    is_correct = models.BooleanField(default=False)
    def __str__(self): return self.choice_text

class Submission(models.Model):
    enrollment = models.ForeignKey(Enrollment,on_delete=models.CASCADE)
    choices = models.ManyToManyField(Choice)
""")
(a/'admin.py').write_text("""from django.contrib import admin
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
""")
v=a/'views.py'
s=v.read_text().replace('from .models import Course, Enrollment','from .models import Course, Enrollment, Question, Choice, Submission')
s+="""
from django.views.decorators.http import require_POST

@require_POST
def submit(request,course_id):
    if not request.user.is_authenticated: return redirect('onlinecourse:login')
    course=get_object_or_404(Course,pk=course_id)
    enrollment=get_object_or_404(Enrollment,user=request.user,course=course)
    ids=[]
    for question in Question.objects.filter(course=course).prefetch_related('choice_set'):
        for choice in question.choice_set.all():
            if str(choice.id) in request.POST.getlist('choice_'+str(question.id)):
                ids.append(choice.id)
    submission=Submission.objects.create(enrollment=enrollment)
    submission.choices.set(ids)
    return redirect('onlinecourse:show_exam_result',course_id=course_id,submission_id=submission.id)

def show_exam_result(request,course_id,submission_id):
    if not request.user.is_authenticated: return redirect('onlinecourse:login')
    course=get_object_or_404(Course,pk=course_id)
    submission=get_object_or_404(Submission,pk=submission_id,enrollment__course=course,enrollment__user=request.user)
    selected_ids=set(submission.choices.values_list('id',flat=True))
    results=[]
    total=possible=0
    for question in Question.objects.filter(course=course).prefetch_related('choice_set'):
        choices=list(question.choice_set.all())
        selected=[c for c in choices if c.id in selected_ids]
        correct=[c for c in choices if c.is_correct]
        ok=bool(correct) and {c.id for c in selected}=={c.id for c in correct}
        possible+=question.grade
        if ok: total+=question.grade
        results.append({'question':question,'choices':choices,'selected':selected,'is_correct':ok})
    grade=100*total/possible if possible else 0
    return render(request,'onlinecourse/exam_result_bootstrap.html',{'course':course,'grade':grade,'total_score':total,'possible_score':possible,'question_results':results})
"""
v.write_text(s)
u=a/'urls.py';s=u.read_text()
s=s.replace('    # <HINT> Create a route for submit view',"    path('<int:course_id>/submit/',views.submit,name='submit'),")
s=s.replace('    # <HINT> Create a route for show_exam_result view',"    path('<int:course_id>/submission/<int:submission_id>/result/',views.show_exam_result,name='show_exam_result'),")
u.write_text(s)
t=a/'templates'/'onlinecourse'
c=t/'course_detail_bootstrap.html';s=c.read_text()
exam="""<div class="card mt-4"><div class="card-header"><h4>Course Assessment</h4></div><div class="card-body">
{% if user.is_authenticated %}
<form method="post" action="{% url 'onlinecourse:submit' course.id %}">{% csrf_token %}
{% for question in course.question_set.all %}
<h5>{{ forloop.counter }}. {{ question.question_text }}</h5><p>Points: {{ question.grade }}</p>
{% for choice in question.choice_set.all %}
<label class="d-block"><input type="checkbox" name="choice_{{ question.id }}" value="{{ choice.id }}"> {{ choice.choice_text }}</label>
{% endfor %}{% empty %}<p>No assessment questions yet.</p>{% endfor %}
<button class="btn btn-primary" type="submit">Submit Exam</button></form>
{% else %}<p>Please log in and enroll first.</p>{% endif %}</div></div>"""
c.write_text(s.replace('<!-- Course detail template changes go here -->',exam))
(t/'exam_result_bootstrap.html').write_text("""<!doctype html><html lang="en"><head><meta charset="utf-8"><title>Exam Results</title>
<link rel="stylesheet" href="https://maxcdn.bootstrapcdn.com/bootstrap/4.5.2/css/bootstrap.min.css"></head>
<body><main class="container mt-4"><h2>{{ course.name }} - Exam Results</h2>
{% if grade > 80 %}<div class="alert alert-success"><h3>Congratulations!</h3><p>You passed the exam.</p></div>
{% else %}<div class="alert alert-warning"><h3>Keep Trying!</h3></div>
<a href="{% url 'onlinecourse:course_details' course.id %}">Re-test</a>{% endif %}
<h4>Score: {{ total_score }} / {{ possible_score }}</h4><p>Grade: {{ grade|floatformat:1 }}%</p>
{% for result in question_results %}<section class="card mb-3"><div class="card-body">
<h5>{{ result.question.question_text }}</h5>
<p>{% if result.is_correct %}Correct{% else %}Incorrect{% endif %}</p>
{% for choice in result.choices %}<p>{% if choice in result.selected %}&#9745;{% else %}&#9744;{% endif %}
{{ choice.choice_text }}{% if choice.is_correct %} (Correct answer){% endif %}</p>{% endfor %}
</div></section>{% endfor %}</main></body></html>""")
settings=p/'myproject'/'settings.py'
s=settings.read_text()
settings.write_text(s+"\nDEFAULT_AUTO_FIELD = 'django.db.models.AutoField'\n")
print('Assessment restoration complete')
