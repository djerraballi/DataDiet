from pyramid.security import Allow, Everyone

class Wiki():
	__name__ = None
	__parent__ = None
	__acl__ = [ (Allow, Everyone, 'view'),
				(Allow, 'user', 'edit')]