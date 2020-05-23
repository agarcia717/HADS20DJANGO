"""
Definition of views.
"""

from django.shortcuts import render,get_object_or_404
from django.http import HttpRequest
from django.template import RequestContext
from datetime import datetime
from django.http.response import HttpResponse, Http404
from django.http import HttpResponseRedirect, HttpResponse
from .models import Question,Choice,User
from django.template import loader
from django.core.urlresolvers import reverse
from app.forms import QuestionForm, ChoiceForm,UserForm
from django.shortcuts import redirect
import json


def home(request):
    """Renders the home page."""
    assert isinstance(request, HttpRequest)
    return render(
        request,
        'app/index.html',
        {
            'title':'Home Page',
            'year':datetime.now().year,
        }
    )

def contact(request):
    """Renders the contact page."""
    assert isinstance(request, HttpRequest)
    return render(
        request,
        'app/contact.html',
        {
            'title':'Autor de la web',
            'message':'Datos de contacto',
            'year':datetime.now().year,
        }
    )

def about(request):
    """Renders the about page."""
    assert isinstance(request, HttpRequest)
    return render(
        request,
        'app/about.html',
        {
            'title':'About',
            'message':'Your application description page.',
            'year':datetime.now().year,
        }
    )


#
def index(request):
    latest_question_list = Question.objects.order_by('-pub_date')
    subjects = {q.subject for q in latest_question_list}
  

    template = loader.get_template('polls/index.html')
    if request.method == "POST":
        subjectPost = request.POST['subject']
        filtered_q_list = latest_question_list.filter(subject = subjectPost)
      
    else:
        subjectPost = ""
        filtered_q_list = latest_question_list
      
    context = {
                'title':'Lista de preguntas de la encuesta',
                'latest_question_list': latest_question_list,
                'subject': subjectPost,
                'filtered_q_list':filtered_q_list,
                'subjects':subjects,
              }
    return render(request, 'polls/index.html', context )
#


def detail(request, question_id):
     question = get_object_or_404(Question, pk=question_id)
     return render(request, 'polls/detail.html', {'title':'Respuestas asociadas a la pregunta:','question': question})

def results(request, question_id, choice_id):
    question = get_object_or_404(Question, pk=question_id)
    choice= get_object_or_404(Choice, pk=choice_id)
    return render(request, 'polls/results.html', {'title':'Resultados de la pregunta:','question': question , 'choice':choice})

def vote(request, question_id):
    p = get_object_or_404(Question, pk=question_id)
    try:
        selected_choice = p.choice_set.get(pk=request.POST['choice'])
    except (KeyError, Choice.DoesNotExist):
        # Vuelve a mostrar el form.
        return render(request, 'polls/detail.html', {
            'question': p,
            'error_message': "ERROR: No se ha seleccionado una opcion",
        })
    else:
        selected_choice.votes += 1
        selected_choice.save()
        # Siempre devolver un HttpResponseRedirect despues de procesar
        # exitosamente el POST de un form. Esto evita que los datos se
        # puedan postear dos veces si el usuario vuelve atras en su browser.
        return HttpResponseRedirect(reverse('results', args=(p.id, selected_choice.id, )))

def question_new(request):
        if request.method == "POST":
            form = QuestionForm(request.POST)
            if form.is_valid():
                question = form.save(commit=False)
                question.pub_date=datetime.now()
                question.save()
                #return redirect('detail', pk=question_id)
                #return render(request, 'polls/index.html', {'title':'Respuestas posibles','question': question})
        else:
            form = QuestionForm()
        return render(request, 'polls/question_new.html', {'form': form})


#
def choice_add(request, question_id):
        question = Question.objects.get(id = question_id)
        if request.method =='POST':
            form = ChoiceForm(request.POST)
            choices = Choice.objects.filter(question=question_id)

            counter = count(choices)
            print("Opciones = ",counter,"\n")

            correctCounter = count(choices.filter(isCorrect=True))
            print("Correctas = ",correctCounter,"\n")

            if form.is_valid(): 
                if counter==4:
                    print("HAY 4 OPCIONES\n")
                    return render(request, 'polls/choice_new.html', {'title':'Pregunta:'+ question.question_text,'form': form,'message':'Esta pregunta ya tiene 4 opciones'})
                elif counter<1:
                    print("HAY MENOS DE 2 OPCIONES")
                    choice = form.save(commit = False)
                    choice.question = question
                    choice.vote = 0
                    choice.save()
                    return render(request, 'polls/choice_new.html', {'title':'Pregunta:'+ question.question_text,'form': form,'message':'Debe tener 2 opciones como mínimo!!'})
                elif counter==3 and correctCounter==0:
                    print("HAY 3 OPCIONES Y NO HAY CORRECTA\n")
                    #tiene que ser correcta
                    choice = form.save(commit = False)
                    choice.question = question
                    choice.isCorrect = True
                    choice.vote = 0
                    choice.save()
                elif counter<4 and correctCounter==1:
                    print("HAY MENOS DE 4 OPCIONES Y HAY CORRECTA\n")
                    #tiene que ser INcorrecta
                    choice = form.save(commit = False)
                    choice.question = question
                    choice.isCorrect = False
                    choice.vote = 0
                    choice.save()
                else:
                    print("HAY MENOS DE 4 OPCIONES Y NO HAY CORRECTA\n")
                    choice = form.save(commit = False)
                    choice.question = question
                    choice.vote = 0
                    choice.save()
                    form.save() 
        else: 
            form = ChoiceForm()
        #return render_to_response ('choice_new.html', {'form': form, 'poll_id': poll_id,}, context_instance = RequestContext(request),)
        return render(request, 'polls/choice_new.html', {'title':'Pregunta:'+ question.question_text,'form': form})
#

def count(i):
    c = 0
    for l in i: c += 1
    return c


def chart(request, question_id):
    q=Question.objects.get(id = question_id)
    qs = Choice.objects.filter(question=q)
    dates = [obj.choice_text for obj in qs]
    counts = [obj.votes for obj in qs]
    context = {
        'dates': json.dumps(dates),
        'counts': json.dumps(counts),
    }

    return render(request, 'polls/grafico.html', context)

def user_new(request):
        if request.method == "POST":
            form = UserForm(request.POST)
            if form.is_valid():
                user = form.save(commit=False)
                user.save()
                #return redirect('detail', pk=question_id)
                #return render(request, 'polls/index.html', {'title':'Respuestas posibles','question': question})
        else:
            form = UserForm()
        return render(request, 'polls/user_new.html', {'form': form})

def users_detail(request):
    latest_user_list = User.objects.order_by('email')
    template = loader.get_template('polls/users.html')
    context = {
                'title':'Lista de usuarios',
                'latest_user_list': latest_user_list,
              }
    return render(request, 'polls/users.html', context)