from topaz.module import ClassDef
from topaz.modules.enumerable import Enumerable
from topaz.objects.objectobject import W_Object


class W_RangeObject(W_Object):
    classdef = ClassDef("Range", W_Object.classdef, filepath=__file__)
    classdef.include_module(Enumerable)

    def __init__(self, space, w_start, w_end, exclusive):
        W_Object.__init__(self, space)
        self.w_start = w_start
        self.w_end = w_end
        self.exclusive = exclusive

    @classdef.method("first")
    @classdef.method("begin")
    def method_begin(self, space):
        return self.w_start

    @classdef.method("last")
    @classdef.method("end")
    def method_end(self, space):
        return self.w_end

    @classdef.method("exclude_end?")
    def method_exclude_end(self, space):
        return space.newbool(self.exclusive)

    classdef.app_method("""
    def each
        unless self.begin.is_a? Integer
            raise TypeError, "can't iterate from Float"
        end
        i = self.begin
        lim = self.end
        lim += 0.1 unless self.exclude_end?
        while i < lim
            yield i
            i += 1
        end
    end

    def ===(value)
        self.include?(value)
    end

    def include?(value)
        beg_compare = self.begin <=> value
        if !beg_compare
            return false
        end
        if beg_compare <= 0
            end_compare = value <=> self.end
            if self.exclude_end?
                return true if end_compare < 0
            else
                return true if end_compare <= 0
            end
        end
        return false
    end
    """)
