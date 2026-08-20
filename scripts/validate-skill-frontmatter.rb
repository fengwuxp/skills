# frozen_string_literal: true

require "yaml"

# Input: repository Skill Markdown files at */SKILL.md.
# Output: unsupported top-level frontmatter fields with a Codex-specific hint.
# Writes/network: none.
module SkillFrontmatterValidator
  ALLOWED_FIELDS = %w[name description].freeze

  module_function

  def validate_skill(path)
    text = File.read(path, encoding: "UTF-8")
    match = text.match(/\A---\n(.*?)\n---\n/m)
    return ["#{path}: missing YAML frontmatter"] unless match

    data = YAML.safe_load(match[1], aliases: true)
    return ["#{path}: YAML frontmatter must be a mapping"] unless data.is_a?(Hash)

    unsupported = data.keys.map(&:to_s).uniq.sort - ALLOWED_FIELDS
    return [] if unsupported.empty?

    [
      "#{path}: unsupported frontmatter field(s): #{unsupported.join(', ')}; " \
      "Codex Skills in this repository only support name and description. " \
      "Use the Codex permission system or existing repository contracts instead.",
    ]
  rescue Psych::SyntaxError => error
    ["#{path}: invalid YAML frontmatter: #{error.message.lines.first.strip}"]
  end

  def validate_root(root)
    Dir.glob(File.join(root, "*", "SKILL.md")).sort.flat_map do |path|
      validate_skill(path)
    end
  end
end

if $PROGRAM_NAME == __FILE__
  root = File.expand_path(ARGV.fetch(0, File.join(__dir__, "..")))
  errors = SkillFrontmatterValidator.validate_root(root)
  unless errors.empty?
    warn errors.join("\n")
    exit 1
  end

  puts "OK Codex Skill frontmatter dialect"
end
