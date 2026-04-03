from enum import Enum, unique


@unique
class DatasetId(str, Enum):
    QW_ADJ_C = "qw_adj_c"
    QW_ADJ_O = "qw_adj_o"
    QW_ADJ_H = "qw_adj_h"
    QW_ADJ_L = "qw_adj_l"
    QW_V = "qw_v"
    QW_MKTCAP = "qw_mktcap"
    QW_K200_YN = "qw_k200_yn"
