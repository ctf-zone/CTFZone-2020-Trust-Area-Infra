import random

class AgentAdapter:
    PKG = 'ctfz.trustarea.checker'
    SVC = 'ctfz.trustarea.checker.ActionsService'
    SECRET = {'__secret__' : 'there-is-no-country-for-an-old-man'}

    def __init__(self, emu):
        self._emu = emu

    def send(self, action, req_id, extras):
        team_id = extras['team_id']
        return self._emu.start_service(
            f'{self.PKG}{team_id}',
            self.SVC, 
            action=action, 
            extras=dict(**self.SECRET, __req_id__=req_id, **extras)
        )

    def echo(self, req_id, team_id, message):
        return self.send('ECHO', req_id, dict(
            team_id=team_id,
            message=message
        ))

    def push_flag(self, req_id, team_id, flag, user_info, description):
        return self.send('PUSH_FLAG', req_id, dict(
            team_id=team_id,
            flag=flag,
            description=description,
            **user_info
        ))


    def pull_flag(self, req_id, team_id, session, task, solution):
        return self.send('PULL_FLAG', req_id, dict(
            team_id=team_id,
            session=session,
            task=task,
            solution=solution
        ))

    def reg_user(self, req_id, team_id, user_info):
        return self.send('REG_USER', req_id, dict(
            team_id=team_id,
            **user_info
        ))

    def check_backup(self, req_id, team_id, session):
        return self.send('CHECK_BACKUP', req_id, dict(
            team_id=team_id,
            session=session
        ))


