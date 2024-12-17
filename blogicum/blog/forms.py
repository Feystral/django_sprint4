from django import forms 
from django.utils.timezone import now

from .models import Post, Comment, Category 


class PostForm(forms.ModelForm):
    class Meta:
        model = Post
        exclude = ['author', 'likes']
        widgets = {
            'pub_date': forms.DateTimeInput(
                attrs={'type': 'datetime-local'},
                format='%Y-%m-%dT%H:%M'
            ),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if not self.initial.get('pub_date'):
            self.initial['pub_date'] = now().strftime('%Y-%m-%dT%H:%M')
        self.fields['category'].queryset = Category.objects.filter(
            is_published=True
        )


class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ['text']
        widgets = {
            'text': forms.Textarea(attrs={'rows': 3}),
        }

    def clean_text(self):
        text = self.cleaned_data.get('text')
        if not text:
            raise forms.ValidationError('Комментарий не может быть пустым.')
        return text
