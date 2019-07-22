# Generated by the protocol buffer compiler.  DO NOT EDIT!
# source: object_detection/protos/square_box_coder.proto

import sys,getpass
_b=sys.version_info[0]<3 and (lambda x:x) or (lambda x:x.encode('latin1'))
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from google.protobuf import reflection as _reflection
from google.protobuf import symbol_database as _symbol_database
# @@protoc_insertion_point(imports)

_sym_db = _symbol_database.Default()




DESCRIPTOR = _descriptor.FileDescriptor(
  name='object_detection/protos/square_box_coder.proto',
  package='object_detection.protos',
  syntax='proto2',
  serialized_options=None,
  serialized_pb=_b('\n.object_detection/protos/square_box_coder.proto\x12\x17object_detection.protos\"S\n\x0eSquareBoxCoder\x12\x13\n\x07y_scale\x18\x01 \x01(\x02:\x02\x31\x30\x12\x13\n\x07x_scale\x18\x02 \x01(\x02:\x02\x31\x30\x12\x17\n\x0clength_scale\x18\x03 \x01(\x02:\x01\x35')
)




_SQUAREBOXCODER = _descriptor.Descriptor(
  name='SquareBoxCoder',
  full_name='object_detection.protos.SquareBoxCoder',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  fields=[
    _descriptor.FieldDescriptor(
      name='y_scale', full_name='object_detection.protos.SquareBoxCoder.y_scale', index=0,
      number=1, type=2, cpp_type=6, label=1,
      has_default_value=True, default_value=float(10),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
    _descriptor.FieldDescriptor(
      name='x_scale', full_name='object_detection.protos.SquareBoxCoder.x_scale', index=1,
      number=2, type=2, cpp_type=6, label=1,
      has_default_value=True, default_value=float(10),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
    _descriptor.FieldDescriptor(
      name='length_scale', full_name='object_detection.protos.SquareBoxCoder.length_scale', index=2,
      number=3, type=2, cpp_type=6, label=1,
      has_default_value=True, default_value=float(5),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
  ],
  extensions=[
  ],
  nested_types=[],
  enum_types=[
  ],
  serialized_options=None,
  is_extendable=False,
  syntax='proto2',
  extension_ranges=[],
  oneofs=[
  ],
  serialized_start=75,
  serialized_end=158,
)

DESCRIPTOR.message_types_by_name['SquareBoxCoder'] = _SQUAREBOXCODER
_sym_db.RegisterFileDescriptor(DESCRIPTOR)

SquareBoxCoder = _reflection.GeneratedProtocolMessageType('SquareBoxCoder', (_message.Message,), dict(
  DESCRIPTOR = _SQUAREBOXCODER,
  __module__ = 'object_detection.protos.square_box_coder_pb2'
  # @@protoc_insertion_point(class_scope:object_detection.protos.SquareBoxCoder)
  ))
_sym_db.RegisterMessage(SquareBoxCoder)


# @@protoc_insertion_point(module_scope)
