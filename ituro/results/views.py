from django.views.generic.list import ListView
from django.views.generic.base import TemplateView
from django.views.generic.detail import DetailView
from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.http import Http404, HttpResponseRedirect
from django.core.urlresolvers import reverse, reverse_lazy
from django.conf import settings
from django.utils.translation import ugettext_lazy as _
from orders.models import LineFollowerStage
from results.models import LineFollowerResult, FireFighterResult, \
    BasketballResult, StairClimbingResult, MazeResult, ColorSelectingResult, \
    SelfBalancingResult, ScenarioResult, InnovativeJuryResult, InnovativeJury, \
    InnovativeTotalResult
from sumo.models import *


RESULTS_DICT = {
    "line_follower": LineFollowerResult,
    "fire_fighter": FireFighterResult,
    "basketball": BasketballResult,
    "stair_climbing": StairClimbingResult,
    "maze": MazeResult,
    "color_selecting": ColorSelectingResult,
    "self_balancing": SelfBalancingResult,
    "scenario": ScenarioResult,
    "innovative": InnovativeJuryResult,
}


class ResultListView(ListView):
    template_name = 'results/result_list.html'

    def dispatch(self, *args, **kwargs):
        category = self.kwargs.get('slug')
        if not category in dict(settings.ALL_CATEGORIES).keys():
            raise Http404
        if not settings.PROJECT_RESULTS or \
           not category in dict(settings.RESULT_CATEGORIES).keys():
            raise PermissionDenied
        if category == 'line_follower':
            return HttpResponseRedirect(
                reverse('line_follower_stage_result_list'))
        elif category == 'micro_sumo':
            return HttpResponseRedirect(reverse('sumo_result_home'))
        elif category == 'innovative':
            return HttpResponseRedirect(reverse('innovative_referee'))

        return super(ResultListView, self).dispatch(*args, **kwargs)

    def get_queryset(self):
        result_model = RESULTS_DICT[self.kwargs.get('slug')]
        return result_model.objects.filter(is_best=True)

    def get_context_data(self, **kwargs):
        context = super(ResultListView, self).get_context_data(**kwargs)
        context['category'] = dict(
            settings.ALL_CATEGORIES)[self.kwargs.get('slug')]

        return context


class LineFollowerStageResultListView(ListView):
    model = LineFollowerStage
    template_name = 'results/line_follower_stage_list.html'

    def dispatch(self, *args, **kwargs):
        if not settings.PROJECT_ORDERS or \
           not "line_follower" in dict(settings.RESULT_CATEGORIES).keys() or \
           not LineFollowerStage.objects.filter(results_available=True).exists():
            raise PermissionDenied
        return super(LineFollowerStageResultListView, self).dispatch(
            *args, **kwargs)

    def get_queryset(self):
        return LineFollowerStage.objects.filter(results_available=True)


class LineFollowerResultListView(ListView):
    model = LineFollowerResult
    template_name = 'results/result_list.html'

    def dispatch(self, *args, **kwargs):
        order = self.kwargs.get("order")
        if not LineFollowerStage.objects.filter(
                order=order, results_available=True).exists():
            return PermissionDenied
        return super(LineFollowerResultListView, self).dispatch(*args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super(LineFollowerResultListView, self).get_context_data(
            **kwargs)
        context['category'] = dict(settings.ALL_CATEGORIES)["line_follower"]
        context['stage'] = LineFollowerStage.objects.filter(
            order=self.kwargs.get("order"))[0]
        return context

    def get_queryset(self):
        return LineFollowerResult.objects.filter(
            stage__order=self.kwargs.get("order"))


class SumoResultHomeView(TemplateView):
    template_name = "results/sumo_home.html"

    def dispatch(self, *args, **kwargs):
        if not "micro_sumo" in dict(settings.RESULT_CATEGORIES).keys():
            raise PermissionDenied
        return super(SumoResultHomeView, self).dispatch(*args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super(SumoResultHomeView, self).get_context_data(**kwargs)
        context["groups"] = settings.SUMO_GROUP_RESULTS
        context["stages"] = settings.SUMO_STAGE_RESULTS
        context["final"] = settings.SUMO_FINAL_RESULTS
        return context


class SumoResultGroupListView(ListView):
    model = SumoGroup
    template_name = 'results/sumo_group_list.html'

    def dispatch(self, *args, **kwargs):
        if not settings.SUMO_GROUP_RESULTS:
            raise PermissionDenied
        return super(SumoResultGroupListView, self).dispatch(*args, **kwargs)

    def get_queryset(self):
        return SumoGroup.objects.filter(is_final=False)


class SumoResultGroupDetailView(DetailView):
    model = SumoGroup
    template_name = "results/sumo_group_detail.html"

    def dispatch(self, *args, **kwargs):
        if not settings.SUMO_GROUP_RESULTS:
            raise PermissionDenied
        return super(SumoResultGroupDetailView, self).dispatch(*args, **kwargs)

    def get_context_data(self, **kwargs):
        group = self.get_object()
        context = super(SumoResultGroupDetailView, self).get_context_data(
            **kwargs)
        context["matches"] = SumoGroupMatch.objects.filter(group=group)
        context["teams"] = SumoGroupTeam.objects.filter(group=group)
        return context


class SumoResultStageListView(ListView):
    model = SumoStage
    template_name = "results/sumo_stage_list.html"

    def dispatch(self, *args, **kwargs):
        if not settings.SUMO_STAGE_RESULTS:
            raise PermissionDenied
        return super(SumoResultStageListView, self).dispatch(*args, **kwargs)


class SumoResultStageDetailView(ListView):
    model = SumoStageMatch
    template_name = "results/sumo_stage_detail.html"

    def dispatch(self, *args, **kwargs):
        if not settings.SUMO_STAGE_RESULTS:
            raise PermissionDenied
        return super(SumoResultStageDetailview, self).dispatch(*args, **kwargs)

    def get_queryset(self):
        return SumoStageMatch.objects.filter(stage__pk=self.kwargs.get("pk"))


class SumoResultFinalDetailView(TemplateView):
    template_name = "results/sumo_final.html"

    def dispatch(self, *args, **kwargs):
        if not settings.SUMO_FINAL_RESULTS:
            raise PermissionDenied
        return super(SumoResultFinalDetailView, self).dispatch(*args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super(SumoResultFinalDetailView, self).dispatch(
            *args, **kwargs)
        group = SumoGroup.objects.filter(is_final=True).first()
        context["group"] = group
        context["matches"] = SumoGroupMatch.objects.filter(group=group)
        return context


class InnovativeResultView(ListView):
    template_name = "results/innovative_result.html"

    def dispatch(self, *args, **kwargs):
        return super(InnovativeResultView, self).dispatch(*args, **kwargs)

    def get_queryset(self):
        return InnovativeTotalResult.objects.filter(project__is_confirmed=True).order_by("-score")

    def get_context_data(self, **kwargs):
        category = self.kwargs.get('slug')
        context = super(InnovativeResultView, self).get_context_data(**kwargs)
        context['category'] = dict(settings.ALL_CATEGORIES)["innovative"]
        return context
