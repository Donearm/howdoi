require 'formula'

class Howdoi < Formula
  homepage 'https://github.com/gleitz/howdoi/'
  url 'http://pypi.python.org/packages/source/h/howdoi/howdoi-1.1.tar.gz'
  sha1 '6a7111a77e42ad99c906b376029b344f2c3c9a87'

  def install
    setup_args = ['setup.py', 'install']
    system "python", *setup_args
  end
end
