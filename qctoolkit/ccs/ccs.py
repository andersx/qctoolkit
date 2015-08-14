#from qctoolkit import *
import qctoolkit as qtk
import numpy as np
#from geometry import *
#from utilities import *
import re, copy, sys, os
from compiler.ast import flatten
import xml.etree.ElementTree as ET
import random

class MoleculeSpanXML(object):
  def __init__(self, parameter_file, **kwargs):
    if 'xyz' in kwargs:
      self.structure = qtk.Molecule()
      self.structure.read_xyz(kwargs['xyz'])

class MoleculeSpan(object):
  def __init__(self, xyz_file, parameter_file, **kwargs):
    self.structure = qtk.Molecule()
    self.structure.read(xyz_file)
    # mutation related variables
    self.mutation_list = []
    self.mutation_target = []
    # stretching related variables
    self.stretching_list = []
    self.stretching_direction = []
    self.stretching_range = []
    # rotation related variables
    self.rotation_list = []
    self.rotation_center = []
    self.rotation_axis = []
    self.rotation_range = []
    # replacing realted variables
    # not yet implemented

    # constraint variables #
    self.constraint = False
    self.forbiden_bonds = []
    self.ztotal = 0
    self.vtotal = 0

    # setup all parameters
    self.read_param(parameter_file)
    self.coor = flatten([
                 ['m' for _ in flatten(self.mutation_list)],
                 ['s' for _ in flatten(self.stretching_list)],
                 ['r' for _ in flatten(self.rotation_list)],
                ])

    MList = self.mutation_list
    _flatten = [item for sublist in MList for item in sublist]
    vlen = np.vectorize(len)
    try:
      lenList = vlen(MList)
    except TypeError:
      lenList = [len(MList[0]) for i in range(len(MList))]

    if not qtk.setting.quiet:
      print "===== CCS REPORT ====="
      qtk.report("generating molecule", xyz_file)
      qtk.report("ccs parameter file", parameter_file)
      qtk.report("mutation indices", self.mutation_list)
      qtk.report("target atomic numbers", self.mutation_target)
      qtk.report("length of mutation vector",
             len(_flatten), "<=>", lenList)
      print ""
      qtk.report("stretching indices", self.stretching_list)
      qtk.report("stretching range", self.stretching_range)
      qtk.report("stretching direction indices",
             self.stretching_direction)
      print ""
      qtk.report("rotation indices", self.rotation_list)
      qtk.report("rotation center", self.rotation_center)
      qtk.report("rotation axis", self.rotation_axis)
      qtk.report("rotation range", self.rotation_range)
      print ""
      qtk.status("ccs coordinate", self.coor)
      print "========= END ========\n"


  # !!!!! TODO !!!!! #
  # 100 line of read_param can be replace by simple xml reader
  # easier to maintain and extend

  def read_param(self,parameter_file):
    stem, extension = os.path.splitext(parameter_file)
    if extension == '.txt':
      self.read_param_txt(parameter_file)
    elif extension == '.xml':
      self.read_param_xml(parameter_file)
    else:
      pass

  ###############################################
  # read ccs_param to xml element tree directly #
  ###############################################
  def read_param_xml(self, parameter_file):
    tree = ET.parse(parameter_file)
    etroot = tree.getroot()

    # !!!!!!!!!!!!!!!!!!!!!!!!!!!!!
    # read span section of xml file
    def read_span(span):
      # !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
      # convert data string to numerical values
      def str2data(data_string, **kwargs):
        if 'dtype' in kwargs:
          dtype = kwargs['dtype']
        else:
          dtype = 'index'
        _data = re.sub(re.compile('[ \n]*'),'',data_string)\
                .split(',')
        _out_list = []
        if dtype == 'index':
          for ind in _data:
            if re.match(re.compile(".*:.*"), ind):
              ind = map(int, ind.split(":"))
              for i in range(ind[0], ind[1]+1):
                _out_list.append(i)
            else:
              _out_list.append(int(ind))
        elif dtype == 'range':
          _out_list = map(float, _data[0].split(":"))
        return _out_list
      # end of data/string conversion
      for _list in span:
        if _list.attrib['type']=='mutation':
          self.mutation_list.append(str2data(_list.text))
          self.mutation_target.append(str2data(\
            _list.attrib['range']))
        elif _list.attrib['type']=='stretching':
          self.stretching_list.append(str2data(_list.text))
          self.stretching_range.append(str2data(\
            _list.attrib['range'], dtype='range'))
          self.stretching_direction.append(str2data(\
            _list.attrib['fromto_direction_index']))
    # end of reading span section

    # !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
    # read constraint section of xml file
    def read_constraint(constraint):
      for cst in constraint:
        if cst.tag == 'forbiden_bond':
          self.forbiden_bonds.append(sorted(map(int, 
            [cst.attrib['begin'], cst.attrib['end']])))
        elif cst.tag == 'Z_sum':
          self.ztotal = cst.attrib['total']
        elif cst.tag == 've_sum':
          self.vtotal = cst.attrib['total']
        else:
          qtk.exit("constraint '" + cst.tag + \
                   "' is not reconized")
    # end of reading constraint section

    for param in etroot:
      if param.tag == 'span':
        read_span(param)
      elif param.tag == 'constraint':
        self.constraint = True
        read_constraint(param)
  ##### END OF READING PARAM FROM XML #####

  ##########################################
  # GENERATE STRUCTURE FROM CCS COORDINATE #
  ##########################################
  # !!TODO!!
  # interface between mutation and other operations is necessary!
  def generate(self, **kwargs):
    self.new_structure = copy.deepcopy(self.structure)
    if 'mutation' in kwargs:
      self._mutate(kwargs['mutation'])
    if 'stretching' in kwargs:
      self._stretch(kwargs['stretching'])
    if 'rotation' in kwargs:
      self._rotate(kwargs['rotatting'])
    return self.new_structure

  def _mutate(self, mutation):
    for m in xrange(len(mutation)):
      for i in xrange(len(mutation[m])):
        index = self.mutation_list[m][i] - 1
        #target = self.mutation_target[m][mutation[m][i]]
        target = mutation[m][i]
        self.new_structure.Z[index] = target
  def _stretch(self, stretching):
    print stretching
  def _rotate(self, rotation):
    print rotation
  ##### END OF STRUCTURE GENERATION #####

  ################################################
  # TEST A GIVEN STRUCTURE SATISFIED CONSTRAINTS #
  ################################################
  # NOT YET IMPLEMENTED!!!!!
  def onManifold(self,structure):
    if self.constraint:
      return True
    else:
      return True

  ###########################################
  # GENERATE A RANDOM POINT ON CCS MANIFOLD #
  ###########################################
  def random(self, **kwargs):
    # !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
    # generate a random ccs coordinate sequence
    def random_coord(self, mode):
      # determin coordinate type
      if mode == 'mutation':
        _list = self.mutation_list
        _targ = self.mutation_target
        _dtype = int
      elif mode == 'stretching':
        _list = self.stretching_list
        _targ = self.stretching_range
        _dtype = float
      elif mode == 'rotation':
        _list = self.rotation_list
        _targ = self.rotation_range
        _dtype = float

      _vec = []
      for _group, _targp in zip(_list, _targ):
        _subvec = []
        for _atom in _group:
          if _dtype == int:
            _subvec.append(random.choice(_targp))
          elif _dtype == float:
            _subvec.append(random.uniform(_targp[0], _targp[1]))
        _vec.append(_subvec)
      if len(_vec) > 0:
        return _vec
    # end of random coordinate generation

    # !!!!!!!!!!!!!!!!!!!!!!!!!!!
    # loop until a point is found
    while True:
      mut_vec = random_coord(self,'mutation')
      str_vec = random_coord(self,'stretching')
      rot_vec = random_coord(self,'rotation')
      query = {}
      if mut_vec:
        query.update({'mutation':mut_vec})
      if str_vec:
        query.update({'stretching':str_vec})

      new_structure = self.generate(**query)
      if self.onManifold(new_structure):
        break
    # end of loop, i.e. a ccs point is found

    return new_structure, query
  ##### END OF RANDOM CCS POINT #####

  #########################################
  # mating function for genetic algorithm #
  #########################################
  def mate(self, parent1, parent2, mutation_rate):

    def getChild():
      child = {}
      for key in parent1.iterkeys():
        if key == 'mutation':
          child_mut = []
          for i in range(len(parent1[key])):
            # mix two parent
            grp = parent1[key][i]
            index = range(len(grp))
            random.shuffle(index)
            ind1 = index[:len(index)/2]
            if len(index)%2 == 0:
              ind2 = index[len(index)/2:]
              append = -1
            else:
              ind2 = index[len(index)/2:-1]
              append = index[-1]
            new = [parent1[key][i][ind] for ind in ind1]
            new.extend([parent2[key][i][ind] for ind in ind2])
            if append >= 0:
              if random.random() >= 0.5:
                new.append(parent1[key][i][append])
              else:
                new.append(parent2[key][i][append])
            # mutation, loop through each element
            for j in range(len(new)):
              if random.random() < mutation_rate:
                mut_target = [tar \
                  for tar in self.mutation_target[i]\
                  if tar != new[j]]
                new[j] = random.choice(mut_target)
            child_mut.append(new)
          child.update({'mutation':child_mut})
        else:
          qtk.exit("ccs mate function is not yet implemented for "\
                   + key)
      return child

    child = getChild()
    while not self.onManifold(child):
      child = getChild()
    return child
  

  #########################################
  # read ccs_param from plain text format #
  #########################################
  # deprecated. kept for backward sporting
  def read_param_txt(self, parameter_file):
    param = open(parameter_file, 'r')

    mutation_flag = re.compile(".*mutation_list:.*")
    stretching_flag = re.compile(".*stretching_list:.*")
    direction_flag = re.compile(".*direction_index:.*")
    rotation_flag = re.compile(".*rotation_list:.*")
    center_flag = re.compile(".*center_index:.*")
    end_flag = re.compile(".*end.*")

    while True:
      line = param.readline()
      if not line: break
      line = re.sub(re.compile("#.*"),'', line)
      if re.match(mutation_flag, line.lower()):
        while not re.match(end_flag, line):
          line = param.readline().rstrip()
          line = re.sub(re.compile("#.*"),'', line)
          try:
            mlist_str =  re.sub(re.compile("->.*"), "", line)\
                         .split(",")
            tlist_str =  re.sub(re.compile(".*->"), "", line)\
                         .split(",")
            mlist = []
            tlist = []
            for m in mlist_str:
              if re.match(re.compile(".*:.*"), m):
                rangeList = map(int, m.split(":"))
                mmin = rangeList[0]
                mmax = rangeList[1] + 1
                mlist.extend(range(mmin,mmax))
              else:
                mlist.append(int(m))
            for t in tlist_str:
              if re.match(re.compile(".*:.*"), t):
                rangeList = map(int, t.split(":"))
                tmin = rangeList[0]
                tmax = rangeList[1] + 1
                tlist.extend(range(tmin,tmax))
              else:
                tlist.append(int(t))
            self.mutation_list.append(mlist)
            self.mutation_target.append(tlist)
          except ValueError:
            pass
        MList = self.mutation_list
        _flatten = [item for sublist in MList for item in sublist]
        vlen = np.vectorize(len)
        # wired numpy.int32 bug for equal length sublist
        try:
          lenList = vlen(MList)
        except TypeError:
          lenList = [len(MList[0]) for i in range(len(MList))]
      elif re.match(stretching_flag, line.lower()):
        while not re.match(end_flag, line):
          line = param.readline().rstrip()
          line = re.sub(re.compile("#.*"),'', line)
          if re.match(direction_flag, line):
            dlist = map(int, re.sub(re.compile(".*:"),
                                    "", line).split(","))
            self.stretching_direction.append(dlist)
            line = param.readline().rstrip()
            line = re.sub(re.compile("#.*"),'', line)
            try:
              slist = map(int, re.sub(re.compile("->.*"),\
                                      "", line).split(","))
              self.stretching_list.append(slist)
              rlist = map(float, re.sub(re.compile(".*->"),\
                                        "", line).split(':'))
              self.stretching_range.append(rlist)
            except ValueError:
              pass

      elif re.match(rotation_flag, line.lower()):
        while not re.match(end_flag, line):
          line = param.readline()
          line = re.sub(re.compile("#.*"),'', line)
          if re.match(center_flag, line):
            center = int(re.sub(re.compile(".*:"),
                                "", line))
            self.rotation_center.append(center)
            line = param.readline().rstrip()
            line = re.sub(re.compile("#.*"),'', line)
            axis = map(int, re.sub(re.compile(".*:"),
                                   "", line).split(","))
            self.rotation_axis.append(axis)
            line = param.readline().rstrip()
            line = re.sub(re.compile("#.*"),'', line)
            try:
              rolist = map(int, re.sub(re.compile("->.*"),\
                                       "", line).split(","))
              self.rotation_list.append(rolist)
              rglist = map(float, re.sub(re.compile(".*->"),\
                                         "", line).split(':'))
              self.rotation_range.append(rglist)
            except ValueError:
              pass
    param.close()

