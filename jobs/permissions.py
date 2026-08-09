from rest_framework.permissions import BasePermission


class IsRecruiter(BasePermission):
    """
    Only recruiters can create jobs.
    """

    def has_permission(self, request, view):
        return (
            request.user.is_authenticated
            and request.user.user_role == "recruiter"
        )


class IsRecruiterOwner(BasePermission):
    """
    Only the recruiter who owns the job can modify or delete it.
    """

    def has_object_permission(self, request, view, obj):
        return obj.recruiter == request.user