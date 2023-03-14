#!/usr/bin/python3

from collections import namedtuple, deque
from random import randint
from itertools import product

class Rect(namedtuple("_Rect", "x, y, w, h")):
  def __contains__(self, point):
    x, y = point
    return False if (not self.x <= x <= self.x + self.w) or (not self.y <= y <= self.y + self.h) else True

  def split(self):
    w2, h2 = self.w/2, self.h/2
    return [Rect(self.x + w_r, self.y + h_r, w2, h2) for (h_r, w_r) in product([0, h2], [0, w2])]

  def __str__(self):
    return f"[{self.x}, {self.y}, {self.w}, {self.h}]"

class Node:
  def __init__(self, nw=None, ne=None, sw=None, se=None, val=None, bounds=None):
    self.nw, self.ne, self.sw, self.se = nw, ne, sw, se
    self.val = val
    self.bounds = bounds

  def __str__(self):
    return f"<{self.val}, {self.bounds}>"

  @property
  def sons(self):
    return self.nw, self.ne, self.sw, self.se

  @property
  def leaf(self):
    return not any(self.sons)

  def __iter__(self):
    yield self
    for n in filter(None, self.sons):
      yield from n

class QuadTree():
  def __init__(self, data, width, height):
    rect = Rect(0, 0, width, height)
    self.size = 0
    self.root = Node(val=data, bounds=rect)
    if data:
      self._split(self.root)

  def add_node(self, val):
    node = self.search(val)
    node.val.append(val)
    self._split(node)
    self.size += 1

  def _split(self, root):
    node_list = deque([root])
    while node_list:
      node = node_list.popleft()
      if len(node.val) <= 1:
        continue
      if node.leaf:
        rects = node.bounds.split()
        for son, bounds_rect in zip(("nw", "ne", "sw", "se"), rects):
          setattr(node, son, Node(val=[], bounds=bounds_rect))
      for val in node.val:
        for son in node.sons:
          if val in son.bounds:
            son.val.append(val)
            break
      node.val.clear()
      node_list.extend(node.sons)

  def search(self, val):
    if val in self.root.bounds:
      node = self.root
      while not node.leaf:
        for son_s in "nw", "ne", "sw", "se":
          son = getattr(node, son_s)
          if val in son.bounds:
            node = son
            break

      return node

  def __iter__(self):
    yield from self.root

  def assert_correct(self):
    for node in self:
      if node.val:
        assert (node.val[0] in node.bounds)

if  __name__ == "__main__":
  data = [(randint(0, 128), randint(0, 128)) for _ in range(0, 10)]
  qt = QuadTree([], 128.0, 128.0)

  for i, d in enumerate(data, start=1):
    print("Add", d)
    qt.add_node(d)
    qt.assert_correct()
    for node in qt:
      print(node)
    assert i == qt.size
