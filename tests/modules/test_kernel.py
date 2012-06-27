from rupypy.objects.procobject import W_ProcObject

from ..base import BaseRuPyPyTest


class TestKernel(BaseRuPyPyTest):
    def test_puts_nil(self, space, capfd):
        space.execute("puts nil")
        out, err = capfd.readouterr()
        assert out == "nil\n"

    def test_lambda(self, space):
        w_res = space.execute("""
        l = lambda { |x| 3 }
        return [l.class, l.lambda?]
        """)
        w_cls, w_lambda = space.listview(w_res)
        assert w_cls is space.getclassfor(W_ProcObject)
        assert w_lambda is space.w_true

    def test_singleton_methods(self, space):
        w_res = space.execute("""
        class X
        end

        return X.new.singleton_methods
        """)
        assert self.unwrap(space, w_res) == []

        w_res = space.execute("""
        def X.foo
        end

        return X.singleton_methods
        """)
        assert self.unwrap(space, w_res) == ["foo"]

        w_res = space.execute("""
        class Y < X
        end
        return [Y.singleton_methods, Y.singleton_methods(false)]
        """)
        assert self.unwrap(space, w_res) == [["foo"], []]

    def test_raise(self, space):
        with self.raises("RuntimeError", "foo"):
            space.execute("raise 'foo'")
        with self.raises("TypeError", "foo"):
            space.execute("raise TypeError, 'foo'")
        with self.raises("TypeError", "foo"):
            space.execute("fail TypeError, 'foo'")
        with self.raises("TypeError", "exception class/object expected"):
            space.execute("fail nil")
        with self.raises("TypeError", "exception object expected"):
            space.execute("""
            class A
              def exception(msg=nil)
              end
            end
            raise A.new
            """)
        with self.raises("RuntimeError"):
            space.execute("""
            class A
              def exception(msg=nil); RuntimeError.new(msg); end
            end
            raise A.new
            """)

    def test_overriding_raise(self, space):
        w_res = space.execute("""
        class A
          def raise(*args); args; end
          def do_raise; raise 'foo'; end
        end
        return A.new.do_raise
        """)
        assert self.unwrap(space, w_res) == ['foo']

class TestRequire(BaseRuPyPyTest):
    def test_simple(self, space, tmpdir):
        f = tmpdir.join("t.rb")
        f.write("""
        def t(a, b)
            a - b
        end
        """)
        w_res = space.execute("""
        require '%s'

        return t(5, 10)
        """ % str(f))
        assert space.int_w(w_res) == -5

    def test_no_ext(self, space, tmpdir):
        f = tmpdir.join("t.rb")
        f.write("""
        def t(a, b)
            a - b
        end
        """)
        w_res = space.execute("""
        require '%s'

        return t(12, 21)
        """ % str(f)[:-3])
        assert space.int_w(w_res) == -9

    def test_load_path(self, space, tmpdir):
        f = tmpdir.join("t.rb")
        f.write("""
        def t(a, b)
            a - b
        end
        """)
        w_res = space.execute("""
        $LOAD_PATH = ['%s']
        require 't.rb'

        return t(2, 5)
        """ % str(tmpdir))
        assert space.int_w(w_res) == -3

    def test_stdlib_default_load_path(self, space):
        w_res = space.execute("""
        return require 'prettyprint'
        """)
        assert w_res is space.w_true

    def test_nonexistance(self, space):
        with self.raises("LoadError"):
            space.execute("require 'xxxxxxx'")

    def test_already_loaded(self, space, tmpdir):
        f = tmpdir.join("f.rb")
        f.write("""
        @a += 1
        """)

        w_res = space.execute("""
        @a = 0
        require '%s'
        require '%s'
        require '%s'

        return @a
        """ % (str(f), str(f), str(f)))
        assert space.int_w(w_res) == 1
