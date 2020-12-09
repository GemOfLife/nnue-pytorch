import chess
import torch
import feature_block
from collections import OrderedDict
from feature_block import *

NUM_SQ = 64
NUM_PT = 10
NUM_PLANES = (NUM_SQ * NUM_PT + 1)

def orient(is_white_pov: bool, sq: int):
  return (63 * (not is_white_pov)) ^ sq

def halfkp_idx(is_white_pov: bool, king_sq: int, sq: int, p: chess.Piece):
  p_idx = (p.piece_type - 1) * 2 + (p.color != is_white_pov)
  return 1 + orient(is_white_pov, sq) + p_idx * NUM_SQ + king_sq * NUM_PLANES

class Features(FeatureBlock):
  def __init__(self):
    super(Features, self).__init__('HalfKP', 0x5d69d7b8, OrderedDict([('HalfKP', NUM_PLANES * NUM_SQ)]))

  def get_active_features(self, board: chess.Board):
    def piece_features(turn):
      indices = torch.zeros(inputs)
      for sq, p in board.piece_map().items():
        if p.piece_type == chess.KING:
          continue
        indices[halfkp_idx(turn, orient(turn, board.king(turn)), sq, p)] = 1.0
      return indices
    return (piece_features(chess.WHITE), piece_features(chess.BLACK))

class FactorizedFeatures(FeatureBlock):
  def __init__(self):
    super(FactorizedFeatures, self).__init__('HalfKP^', 0x5d69d7b8, OrderedDict([('HalfKP', NUM_PLANES * NUM_SQ), ('HalfK', NUM_SQ), ('P', NUM_SQ * 10 )]))

  def get_active_features(self, board: chess.Board):
    raise Exception('Not supported yet, you must use the c++ data loader for factorizer support during training')

  def get_feature_factors(self, idx):
    if idx >= self.num_real_features:
      raise Exception('Feature must be real')

    k_idx = idx // NUM_PLANES
    p_idx = idx % NUM_PLANES - 1

    return [idx, self.get_factor_base_feature('HalfK') + k_idx, self.get_factor_base_feature('P') + p_idx]

'''
This is used by the features module for discovery of feature blocks.
'''
def get_feature_block_clss():
  return [Features, FactorizedFeatures]
