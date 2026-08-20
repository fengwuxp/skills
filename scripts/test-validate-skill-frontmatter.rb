# frozen_string_literal: true

require "minitest/autorun"
require "fileutils"
require "tmpdir"
require_relative "validate-skill-frontmatter"

class SkillFrontmatterValidatorTest < Minitest::Test
  def write_skill(frontmatter)
    root = Dir.mktmpdir("skill-frontmatter-test-")
    skill = File.join(root, "sample-skill")
    Dir.mkdir(skill)
    path = File.join(skill, "SKILL.md")
    File.write(path, "---\n#{frontmatter}\n---\n\n# Sample\n")
    [root, path]
  end

  def test_accepts_codex_skill_frontmatter
    root, path = write_skill("name: sample-skill\ndescription: Use for sample tasks")
    assert_empty SkillFrontmatterValidator.validate_skill(path)
  ensure
    FileUtils.remove_entry(root) if root
  end

  def test_rejects_platform_specific_fields_with_codex_hint
    root, path = write_skill(
      "name: sample-skill\n" \
      "description: Use for sample tasks\n" \
      "allowed-tools: Bash\n" \
      "hooks:\n" \
      "  - command: echo test",
    )

    errors = SkillFrontmatterValidator.validate_skill(path)
    assert errors.any? { |error| error.include?("allowed-tools") }
    assert errors.any? { |error| error.include?("hooks") }
    assert errors.any? { |error| error.include?("Codex") }
  ensure
    FileUtils.remove_entry(root) if root
  end

  def test_rejects_missing_frontmatter
    root = Dir.mktmpdir("skill-frontmatter-test-")
    skill = File.join(root, "sample-skill")
    Dir.mkdir(skill)
    path = File.join(skill, "SKILL.md")
    File.write(path, "# Sample\n")

    errors = SkillFrontmatterValidator.validate_skill(path)
    assert errors.any? { |error| error.include?("missing YAML frontmatter") }
  ensure
    FileUtils.remove_entry(root) if root
  end
end
