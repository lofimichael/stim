class Stim < Formula
  include Language::Python::Virtualenv

  desc "CLI caffeine tracker with half-life calculations and visualization"
  homepage "https://github.com/lofimichael/stim"
  url "https://github.com/lofimichael/stim/archive/refs/tags/v1.0.0.tar.gz"
  sha256 "0019dfc4b32d63c1392aa264aed2253c1e0c2fb09216f8e2cc269bbfb8bb49b5"
  license "Proprietary Dual-License"

  head do
    if ENV["STIM_DEV"]
      url ".", using: :git, branch: "main"
    else
      url "https://github.com/lofimichael/stim.git", branch: "main"
    end
  end

  depends_on "python@3.11"
  depends_on "python-build" => :build
  depends_on "python-pip" => :build

  resource "plotext" do
    url "https://files.pythonhosted.org/packages/c9/d7/f75f397af966fe252d0d34ffd3cae765317fce2134f925f95e7d6725d1ce/plotext-5.3.2.tar.gz"
    sha256 "52d1e932e67c177bf357a3f0fe6ce14d1a96f7f7d5679d7b455b929df517068e"
  end

  def install
    # Create and activate virtualenv
    venv = virtualenv_create(libexec, "python3.11")

    # Install build dependencies
    system Formula["python-build"].opt_bin/"pip", "install", "build"
    
    # Build the package using pyproject.toml
    system Formula["python-build"].opt_bin/"python", "-m", "build", "--wheel", "--no-isolation", "."
    
    # Install the built wheel and dependencies
    venv.pip_install resources
    venv.pip_install Dir["dist/*.whl"].first
  end

  def caveats
    <<~EOS
      Data is stored in ~/.stim and will persist across updates.
      Free for personal use. Commercial use requires a license. See LICENSE.md for details.
    EOS
  end

  test do
    # Create test environment
    testpath.mkpath
    stim_dir = testpath/".stim"
    stim_dir.mkpath
    ENV["HOME"] = testpath

    # Test basic functionality
    assert_match "Caffeine Tracker", shell_output("#{bin}/stim help")
    
    # Test dose addition
    output = shell_output("#{bin}/stim 100")
    assert_match(/Added.*mg/, output)
    
    # Test history
    assert_match(/mg/, shell_output("#{bin}/stim history"))
    
    # Test visualization
    output = shell_output("#{bin}/stim graph")
    assert_match(/Caffeine Levels/, output)
  end
end 