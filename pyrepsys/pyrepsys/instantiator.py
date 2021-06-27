#

#

import pyrepsys.behavior as behavior
import pyrepsys.reputation as reputation
import pyrepsys.metrics as metrics
from pyrepsys.helpers import ObjectType


class Instantiator:
    def create(self, object_type, classname):
        if object_type is ObjectType.REPUTATION_STRATEGY or object_type is ObjectType.IMPROVEMENT_HANDLER:
            source_module = reputation
        elif object_type is ObjectType.METRIC:
            source_module = metrics
        elif object_type is ObjectType.RATING_STRATEGY or object_type is ObjectType.DISTORT_STRATEGY:
            source_module = behavior
        else:
            raise NotImplementedError

        try:
            instance = getattr(source_module, classname)()
        except AttributeError:
            raise NameError("can't find '{}' in '{}'".format(classname, source_module))
        else:
            return instance