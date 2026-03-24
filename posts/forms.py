from django import forms
from .models import Post, Comment


class PostForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = ['content', 'image', 'video']
        widgets = {
            'content': forms.Textarea(attrs={
                'rows': 3,
                'placeholder': "What's happening?",
                'maxlength': 280,
                'class': 'w-full resize-none bg-transparent outline-none text-gray-800 placeholder-gray-400 text-lg',
            }),
        }


class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ['content']
        widgets = {
            'content': forms.Textarea(attrs={
                'rows': 2,
                'placeholder': 'Add a comment...',
                'maxlength': 280,
                'class': 'w-full resize-none bg-transparent outline-none text-gray-800 placeholder-gray-400',
            }),
        }
