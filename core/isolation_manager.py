class IsolationManager:
    @staticmethod
    def check_access(user_id, project_id, db):
        from database.models import Project
        p = db.query(Project).filter(Project.id == project_id).first()
        return p and p.leader_id == user_id
