import torch
import torch.nn.functional as F


class _BlockDiagonalMask:
    def __init__(self, q_seqlen, kv_seqlen=None):
        self.q_seqlen = [int(x) for x in q_seqlen]
        self.kv_seqlen = [int(x) for x in (kv_seqlen if kv_seqlen is not None else q_seqlen)]

    @classmethod
    def from_seqlens(cls, q_seqlen, kv_seqlen=None):
        return cls(q_seqlen, kv_seqlen)


class fmha:
    BlockDiagonalMask = _BlockDiagonalMask


def _sdpa(q, k, v):
    # entrada [B, M, H, K] como xformers; SDPA espera [B, H, M, K]
    return F.scaled_dot_product_attention(q.transpose(1, 2), k.transpose(1, 2), v.transpose(1, 2)).transpose(1, 2)


def memory_efficient_attention(q, k, v, attn_bias=None, p=0.0, scale=None):
    if attn_bias is None:
        return _sdpa(q, k, v)
    assert isinstance(attn_bias, _BlockDiagonalMask) and q.shape[0] == 1
    out, qo, ko = [], 0, 0
    for ql, kl in zip(attn_bias.q_seqlen, attn_bias.kv_seqlen):
        out.append(_sdpa(q[:, qo:qo + ql], k[:, ko:ko + kl], v[:, ko:ko + kl]))
        qo += ql; ko += kl
    return torch.cat(out, dim=1)
