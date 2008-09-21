from django import forms

from plan.common.models import *

class CourseForm(forms.Form):
    courses = forms.models.ModelMultipleChoiceField(Course.objects.all())

class LectureForm(forms.models.ModelForm):
    class Meta:
        model = Lecture

class GroupForm(forms.Form):
    groups = forms.models.ModelMultipleChoiceField(Group.objects.all(), required=False)

    def __init__(self, queryset, *args, **kwargs):
        super(GroupForm, self).__init__(*args, **kwargs)

        self.fields['groups'].queryset = queryset
        self.fields['groups'].widget.attrs['size'] = 5

class DeadlineForm(forms.models.ModelForm):
    class Meta:
        model = Deadline

    def __init__(self, queryset, *args, **kwargs):
        super(DeadlineForm, self).__init__(*args, **kwargs)

        self.fields['userset'].queryset = queryset
        self.fields['userset'].widget.attrs['style'] = 'width: 7em'
        self.fields['time'].widget.attrs['style'] = 'width: 3em'
        self.fields['date'].widget.attrs['style'] = 'width: 6em'
