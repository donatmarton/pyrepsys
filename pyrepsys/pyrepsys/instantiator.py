#

#

import pyrepsys.behavior as behavior
import pyrepsys.reputation as reputation
import pyrepsys.metrics as metrics


class Instantiator:
    def create_reputation_strategy(self, classname):
        return self._create(reputation, classname)

    def create_improvement_handler(self, classname):
        return self._create(reputation, classname)

    def create_metric(self, classname):
        return self._create(metrics, classname)

    def create_rating_strategy(self, classname):
        return self._create(behavior, classname)

    def create_distort_strategy(self, classname):
        return self._create(behavior, classname)

    def _create(self, source_module, classname):
        try:
            instance = getattr(source_module, classname)()
        except AttributeError:
            raise NameError("can't find '{}' in '{}'".format(classname, source_module))
        else:
            return instance