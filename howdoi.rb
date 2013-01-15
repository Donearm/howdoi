require 'formula'

class Howdoi < Formula
  homepage 'https://github.com/gleitz/howdoi/'
  url 'http://pypi.python.org/packages/source/h/howdoi/howdoi-1.0.tar.gz'
  sha1 'a074e523b7e00c5ab42b9539694bc37071d3363c'

  def install
    setup_args = ['setup.py', 'install']
    system "python", *setup_args
  end
end
