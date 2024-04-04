from typing import Callable
from absl.testing import absltest
from absl.testing import parameterized
import torch
import torch_xla2
import torch_xla2.functions
import torch_xla2.tensor

class TestTorchFunctions(parameterized.TestCase):
  @parameterized.named_parameters(
    ('tensor_2d', lambda: torch.tensor([[0.1, 1.2], [2.2, 3.1], [4.9, 5.2]])),
    ('tensor_1d', lambda: torch.tensor([0, 1],)),
    ('tensor_scalar', lambda: torch.tensor(3.14159,)),
    ('tensor_empty', lambda: torch.tensor([],)),
    ('ones_2d', lambda: torch.ones(2, 3)),
    ('ones_1d', lambda: torch.ones(5)),
    ('zeros_2d', lambda: torch.zeros(2, 3)),
    ('zeros_1d', lambda: torch.zeros(5)),
    ('eye_3x3', lambda: torch.eye(3)),
    ('eye_4x2', lambda: torch.eye(4, 2)),
    ('full_tuple', lambda: torch.full((2, 3), 3.141592)),
  )
  def test_tensor_constructor(self, func: Callable[[], torch.Tensor]):
    expected = func()

    with torch_xla2.functions.XLAFunctionMode():
      actual = func()
      self.assertIsInstance(actual, torch_xla2.tensor.XLATensor2)

    # TODO: dtype is actually important
    torch.testing.assert_close(torch_xla2.tensor.j2t(actual._elem), expected, check_dtype=False)


if __name__ == '__main__':
  absltest.main()
