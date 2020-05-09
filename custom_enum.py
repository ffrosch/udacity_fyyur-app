import enum

class GenreEnum(enum.Enum):
  alternative = 'Alternative'
  blues = 'Blues'
  classical = 'Classical'
  country = 'Country'
  electronic = 'Electronic'
  folk = 'Folk'
  funk = 'Funk'
  hip_hop = 'Hip-Hop'
  heavy_metal = 'Heavy Metal'
  instrumental = 'Instrumental'
  jazz = 'Jazz'
  musical_theatre = 'Musical Theatre'
  pop = 'Pop'
  punk = 'Punk'
  rnb = 'R&B'
  reggae = 'Reggae'
  rocknroll = 'Rock n Roll'
  soul = 'Soul'
  other = 'Other'
  
  def __repr__(self):
    return f'{self.value}'
  
  def __str__(self):
    return f'{self.value}'


class StateEnum(enum.Enum):
  AL = 'AL'
  AK = 'AK'
  AZ = 'AZ'
  AR = 'AR'
  CA = 'CA'
  CO = 'CO'
  CT = 'CT'
  DE = 'DE'
  DC = 'DC'
  FL = 'FL'
  GA = 'GA'
  HI = 'HI'
  ID = 'ID'
  IL = 'IL'
  IN = 'IN'
  IA = 'IA'
  KS = 'KS'
  KY = 'KY'
  LA = 'LA'
  ME = 'ME'
  MT = 'MT'
  NE = 'NE'
  NV = 'NV'
  NH = 'NH'
  NJ = 'NJ'
  NM = 'NM'
  NY = 'NY'
  NC = 'NC'
  ND = 'ND'
  OH = 'OH'
  OK = 'OK'
  OR = 'OR'
  MD = 'MD'
  MA = 'MA'
  MI = 'MI'
  MN = 'MN'
  MS = 'MS'
  MO = 'MO'
  PA = 'PA'
  RI = 'RI'
  SC = 'SC'
  SD = 'SD'
  TN = 'TN'
  TX = 'TX'
  UT = 'UT'
  VT = 'VT'
  VA = 'VA'
  WA = 'WA'
  WV = 'WV'
  WI = 'WI'
  WY = 'WY'
  
  def __repr__(self):
    return f'{self.value}'
  
  def __str__(self):
    return f'{self.value}'