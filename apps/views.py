"""Demo code for the controllers."""
import json
from django.views.generic.detail import DetailView
from django.contrib.auth.models import User
from django.views.generic import TemplateView, ListView
from django.views.generic.edit import CreateView, UpdateView
from users.forms import UserPlanCreateForm
from djstripe.models import Plan
import stripe
from django.conf import settings
from django.utils.decorators import method_decorator
from .decorators import administration_required
from django.core.urlresolvers import reverse_lazy
from django.contrib.auth.decorators import login_required


class PlanBaseViewMixin(object):
    """Plan mixin."""

    model = Plan
    pk_url_kwarg = 'plan_id'

    @method_decorator(login_required)
    @method_decorator(administration_required, name='dispatch')
    def dispatch(self, request, *args, **kwargs):
        """Dispatch method."""
        return super(PlanBaseViewMixin, self).dispatch(request, *args, **kwargs)


class PostDetailView(PlanBaseViewMixin, DetailView):
    """Post detail views."""

    template_name = "users/user_post_details.html"
    model = User

    def get_context_data(self, **kwargs):
        """Customize context data."""
        context = super(PostDetailView, self).get_context_data(**kwargs)
        context['base_portal'] = self.request.user.profile.get_base_portal()
        return context


class PostView(TemplateView):
    """Return user's posts."""

    template_name = "users/post.html"
    model = User

    def get_context_data(self, **kwargs):
        """Customize context data."""
        context = super(PostView, self).get_context_data(**kwargs)
        tracker_list = self.request.user.profile.get_graph_source_data()
        context['base_portal'] = self.request.user.profile.get_base_portal()
        context["tracker_list"] = json.dumps(tracker_list)

        return context


class PlanListView(ListView):
    """Return the list of all plans."""

    template_name = "users/plan_list.html"
    model = Plan

    def get_context_data(self, **kwargs):
        """Customize context data."""
        context = super(PlanListView, self).get_context_data(**kwargs)
        return context

    def get_queryset(self):
        """Customize queryset method."""
        stripe.api_key = settings.STRIPE_TEST_SECRET_KEY
        plan_list = stripe.Plan.list()
        [Plan.sync_from_stripe_data(pl) for pl in plan_list['data']]
        return Plan.objects.all()


class PlanCreate(PlanBaseViewMixin, CreateView):
    """Plan view for creating an new object instance."""

    template_name = "plans/create_plan.html"
    form_class = UserPlanCreateForm
    success_url = reverse_lazy('dashboard_plans')

    def form_valid(self, form):
        """
        Check form validation.

        # We make sure to call the parent's form_valid() method because
        # it might do some processing (in the case of CreateView, it will
        # call form.save() for example).
        """
        self.object = form.save(commit=False)
        self.object.user = self.request.user
        response = super(PlanCreate, self).form_valid(form)
        return response


class PlanUpdate(PlanBaseViewMixin, UpdateView):
    """Updating an plan object."""

    template_name = "plans/edit_plan.html"
    model = Plan
    success_url = reverse_lazy('dashboard_plans')
    fields = '__all__'

    def form_valid(self, form):
        """
        Check form validation.

        # We make sure to call the parent's form_valid() method because
        # it might do some processing (in the case of CreateView, it will
        # call form.save() for example).
        """
        self.object = form.save(commit=False)
        self.object.user = self.request.user
        response = super(PlanUpdate, self).form_valid(form)
        return response
