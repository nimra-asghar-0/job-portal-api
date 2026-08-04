from rest_framework.permissions import BasePermission


class IsCandidate(BasePermission):
    """
    Only users with the candidate role can apply for jobs.
    """

    def has_permission(self, request, view):
        return (
            request.user.is_authenticated
            and request.user.user_role == "candidate"
        )


class IsRecruiter(BasePermission):
    """
    Only users with the recruiter role can manage applications.
    """

    def has_permission(self, request, view):
        return (
            request.user.is_authenticated
            and request.user.user_role == "recruiter"
        )