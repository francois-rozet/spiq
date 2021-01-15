r"""Peak Signal-to-Noise Ratio (PSNR)

This module implements the PSNR in PyTorch.

Wikipedia:
    https://en.wikipedia.org/wiki/Peak_signal-to-noise_ratio
"""

import torch
import torch.nn as nn

from piqa.utils import _jit, build_reduce

from typing import List


@_jit
def mse(x: torch.Tensor, y: torch.Tensor) -> torch.Tensor:
    r"""Returns the Mean Squared Error (MSE) between \(x\) and \(y\).

    $$ \text{MSE}(x, y) = \frac{1}{\text{size}(x)} \sum_i (x_i - y_i)^2 $$

    Args:
        x: An input tensor, \((N, *)\).
        y: A target tensor, \((N, *)\).

    Returns:
        The MSE vector, \((N,)\).

    Example:
        >>> x = torch.rand(5, 3, 256, 256)
        >>> y = torch.rand(5, 3, 256, 256)
        >>> l = mse(x, y)
        >>> l.size()
        torch.Size([5])
    """

    return ((x - y) ** 2).view(x.size(0), -1).mean(-1)


@_jit
def psnr(
    x: torch.Tensor,
    y: torch.Tensor,
    value_range: float = 1.,
    epsilon: float = 1e-8,
) -> torch.Tensor:
    r"""Returns the PSNR between \(x\) and \(y\).

    $$ \text{PSNR}(x, y) =
        10 \log_{10} \left( \frac{L^2}{\text{MSE}(x, y)} \right) $$

    Args:
        x: An input tensor, \((N, *)\).
        y: A target tensor, \((N, *)\).
        value_range: The value range \(L\) of the inputs (usually 1. or 255).
        epsilon: A numerical stability term.

    Returns:
        The PSNR vector, \((N,)\).

    Example:
        >>> x = torch.rand(5, 3, 256, 256)
        >>> y = torch.rand(5, 3, 256, 256)
        >>> l = psnr(x, y)
        >>> l.size()
        torch.Size([5])
    """

    return 10 * torch.log10(value_range ** 2 / (mse(x, y) + epsilon))


class PSNR(nn.Module):
    r"""Creates a criterion that measures the PSNR
    between an input and a target.

    Args:
        reduction: Specifies the reduction to apply to the output:
            `'none'` | `'mean'` | `'sum'`.

        `**kwargs` are transmitted to `psnr`.

    Shapes:
        * Input: \((N, *)\)
        * Target: \((N, *)\)
        * Output: \((N,)\) or \(()\) depending on `reduction`

    Example:
        >>> criterion = PSNR()
        >>> x = torch.rand(5, 3, 256, 256, requires_grad=True).cuda()
        >>> y = torch.rand(5, 3, 256, 256, requires_grad=True).cuda()
        >>> l = criterion(x, y)
        >>> l.size()
        torch.Size([])
        >>> l.backward()
    """

    def __init__(self, reduction: str = 'mean', **kwargs):
        r""""""
        super().__init__()

        self.reduce = build_reduce(reduction)
        self.kwargs = kwargs

    def forward(
        self,
        input: torch.Tensor,
        target: torch.Tensor,
    ) -> torch.Tensor:
        r"""Defines the computation performed at every call.
        """

        l = psnr(input, target, **self.kwargs)

        return self.reduce(l)
