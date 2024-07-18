import factory

from factory.django import DjangoModelFactory
from .models import Section, Guide, Feedback
from users.factory import UserFactory

class SectionFactory(DjangoModelFactory):
    class Meta:
        model = Section
    
    name = factory.Faker("name")
    slug = factory.LazyAttribute(lambda obj: obj.name.lower().replace(" ", "-"))


class GuideFactory(DjangoModelFactory):
    class Meta:
        model = Guide

    author = factory.SubFactory(UserFactory)
    section = factory.SubFactory(SectionFactory)

    title = factory.Faker("name")
    slug = factory.LazyAttribute(lambda obj: obj.title.lower().replace(" ", "-").replace(".", "-"))



class FeedbackFactory(DjangoModelFactory):
    class Meta:
        model = Feedback

    guide = factory.SubFactory(GuideFactory)
    user = factory.SubFactory(UserFactory)
    upvote = factory.Faker("boolean")
