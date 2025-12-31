"""
Views for study set generation and viewing.
"""

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import HttpResponseForbidden, JsonResponse

from .models import StudySet, Flashcard, QuizQuestion
from .forms import GenerateStudySetForm
from .ai_service import generate_flashcards, generate_quiz, extract_text_from_pdf


@login_required
def generate_view(request, set_type):
    """
    Generate a new study set (flashcards or quiz).
    set_type: 'flashcards' or 'quiz'
    """
    if set_type not in ['flashcards', 'quiz']:
        return redirect('home')

    if request.method == 'POST':
        form = GenerateStudySetForm(request.POST, request.FILES)

        if form.is_valid():
            input_type = form.cleaned_data['input_type']
            count = form.cleaned_data['count']
            title = form.cleaned_data['title']

            # Get text content
            if input_type == 'pdf':
                pdf_result = extract_text_from_pdf(request.FILES['pdf_file'])
                if not pdf_result['success']:
                    messages.error(request, pdf_result['error'])
                    return render(request, 'study/generate.html', {
                        'form': form,
                        'set_type': set_type
                    })
                text = pdf_result['text']
            else:
                text = form.cleaned_data['text_content']

            # Generate content using AI
            if set_type == 'flashcards':
                result = generate_flashcards(text, count)
            else:
                result = generate_quiz(text, count)

            if not result['success']:
                messages.error(request, result['error'])
                return render(request, 'study/generate.html', {
                    'form': form,
                    'set_type': set_type
                })

            # Create StudySet
            study_set = StudySet.objects.create(
                owner=request.user,
                set_type=set_type,
                language=result['language'],
                title=title,
                source_text=text[:5000]  # Limit stored text
            )

            # Create items
            if set_type == 'flashcards':
                for i, card in enumerate(result['flashcards']):
                    Flashcard.objects.create(
                        study_set=study_set,
                        index=i,
                        question=card['question'],
                        answer=card['answer']
                    )
            else:
                for i, q in enumerate(result['questions']):
                    QuizQuestion.objects.create(
                        study_set=study_set,
                        index=i,
                        question=q['question'],
                        options=q['options'],
                        correct_index=q['correctIndex'],
                        explanation=q['explanation']
                    )

            messages.success(request, 'تم إنشاء المجموعة بنجاح!')
            return redirect('study:detail', pk=study_set.pk)

    else:
        form = GenerateStudySetForm(initial={'set_type': set_type})

    return render(request, 'study/generate.html', {
        'form': form,
        'set_type': set_type
    })


@login_required
def study_set_detail(request, pk):
    """View a study set (flashcards or quiz)."""
    study_set = get_object_or_404(StudySet, pk=pk)

    # Check access: owner can always view, others only if shared
    if study_set.owner != request.user:
        if not study_set.is_shared:
            return HttpResponseForbidden('ليس لديك صلاحية لعرض هذه المجموعة.')

    context = {
        'study_set': study_set,
        'is_owner': study_set.owner == request.user,
    }

    if study_set.set_type == 'flashcards':
        context['flashcards'] = study_set.flashcards.all()
        return render(request, 'study/flashcards_view.html', context)
    else:
        context['questions'] = study_set.questions.all()
        return render(request, 'study/quiz_view.html', context)


@login_required
def history_view(request):
    """View user's study set history."""
    study_sets = StudySet.objects.filter(
        owner=request.user
    ).order_by('-created_at')

    # Filter by type if specified
    set_type = request.GET.get('type')
    if set_type in ['flashcards', 'quiz']:
        study_sets = study_sets.filter(set_type=set_type)

    return render(request, 'study/history.html', {
        'study_sets': study_sets,
        'current_type': set_type,
    })


@login_required
def delete_study_set(request, pk):
    """Delete a study set."""
    study_set = get_object_or_404(StudySet, pk=pk, owner=request.user)

    if request.method == 'POST':
        study_set.delete()
        messages.success(request, 'تم حذف المجموعة بنجاح.')
        return redirect('study:history')

    return render(request, 'study/confirm_delete.html', {
        'study_set': study_set
    })


@login_required
def study_set_json(request, pk):
    """Return study set data as JSON (for HTMX picker)."""
    study_set = get_object_or_404(StudySet, pk=pk, owner=request.user)

    data = {
        'id': study_set.pk,
        'type': study_set.set_type,
        'type_display': study_set.get_set_type_display(),
        'language': study_set.language,
        'title': study_set.title or 'بدون عنوان',
        'item_count': study_set.item_count,
        'created_at': study_set.created_at.strftime('%Y-%m-%d'),
        'is_shared': study_set.is_shared,
    }

    # Add preview
    if study_set.set_type == 'flashcards':
        first_card = study_set.flashcards.first()
        if first_card:
            data['preview'] = first_card.question[:100]
    else:
        first_q = study_set.questions.first()
        if first_q:
            data['preview'] = first_q.question[:100]

    return JsonResponse(data)
