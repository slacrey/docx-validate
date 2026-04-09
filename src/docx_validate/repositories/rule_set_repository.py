from sqlalchemy.orm import Session

from docx_validate.models.rule_set import DetectionRuleSet


class RuleSetRepository:
    def __init__(self, session: Session) -> None:
        self.session = session

    def create(self, rule_set: DetectionRuleSet) -> DetectionRuleSet:
        self.session.add(rule_set)
        self.session.commit()
        self.session.refresh(rule_set)
        return rule_set

    def get(self, rule_set_id: int) -> DetectionRuleSet | None:
        return self.session.get(DetectionRuleSet, rule_set_id)
