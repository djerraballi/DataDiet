from pyramid.security import Allow, Everyone

USERS = {'anonymous':'anonymous',
			'user':'user'}

__acl__ = [ (Allow, Everyone, 'view'),
				(Allow, 'user', 'edit')]

def log_check(userid, request):
	if userid in USERS:
		return userid, 'edit'
	else:
		return None, 'view'
