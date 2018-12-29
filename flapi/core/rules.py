from typing import Callable, Dict


class Rule:
    def __call__(self, item: Dict) -> bool:
        raise NotImplementedError


class _CollectionRule(Rule):
    def __init__(self, *rules: Rule):
        self.rules = rules

    def __call__(self, item: Dict) -> bool:
        raise NotImplementedError


class AnyOf(_CollectionRule):
    def __call__(self, item: Dict) -> bool:
        return any(rule(item) for rule in self.rules)


class AllOf(_CollectionRule):
    def __call__(self, item: Dict) -> bool:
        return all(rule(item) for rule in self.rules)


class NoneOf(_CollectionRule):
    def __call__(self, item: Dict) -> bool:
        return not any(rule(item) for rule in self.rules)


class Callback(AllOf):
    def __init__(self, *funcs: Callable):
        super(Callback, self).__init__(*funcs)
