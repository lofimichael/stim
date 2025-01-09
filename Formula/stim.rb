class Stim < Formula
  include Language::Python::Virtualenv

  desc "CLI caffeine tracker with half-life calculations and visualization"
  homepage "https://github.com/lofimichael/stim"
  url "https://github.com/lofimichael/stim/archive/refs/tags/v1.0.0.tar.gz"
  sha256 "0686f5393cd46b13a9fbe399a88a50dda0f7f1da2583dea994cff7da6db3b5b9"
  license "Proprietary Dual-License"

  head do
    url ".", using: :git, branch: "main"
    version "HEAD"
  end

  depends_on "python@3.11"

  resource "plotext" do
    url "https://files.pythonhosted.org/packages/c9/d7/f75f397af966fe252d0d34ffd3cae765317fce2134f925f95e7d6725d1ce/plotext-5.3.2.tar.gz"
    sha256 "52d1e932e67c177bf357a3f0fe6ce14d1a96f7f7d5679d7b455b929df517068e"
  end

  def install
    virtualenv_create(libexec, "python3.11")
    virtualenv_install_with_resources
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