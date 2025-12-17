from dataclasses import dataclass, field, fields
from typing import Dict, Any


@dataclass
class BaseCocoObject:
    metadata: Dict[str, Any] = field(default_factory=dict)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'BaseCocoObject':
        known_fields = {f.name for f in fields(cls)}
        init_args = {}
        extra_data = {}
        for key, value in data.items():
            if key in known_fields:
                init_args[key] = value
            else:
                extra_data[key] = value
        if 'metadata' in init_args:
            extra_data.update(init_args.pop('metadata'))

        return cls(**init_args, metadata=extra_data)

    def to_dict(self) -> Dict[str, Any]:
        result = {}
        for f in fields(self):
            if f.name == 'metadata':
                continue
            value = getattr(self, f.name)
            if isinstance(value, BaseCocoObject):
                value = value.to_dict()
            elif isinstance(value, list):
                value = [
                    item.to_dict() if isinstance(item, BaseCocoObject) else item
                    for item in value
                ]
            if value is not None:
                result[f.name] = value
        result.update(self.metadata)
        return result