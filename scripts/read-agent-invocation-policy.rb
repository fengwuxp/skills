# frozen_string_literal: true

require "yaml"
require "json"

# Input: one agents/openai.yaml path. Output: the effective boolean policy as JSON.
# Writes/network: none. Invalid, duplicate, or ambiguous policy data exits non-zero.
def reject_duplicate_keys(node)
  if node.is_a?(Psych::Nodes::Mapping)
    seen = {}
    node.children.each_slice(2) do |key, _value|
      unless key.is_a?(Psych::Nodes::Scalar)
        raise ArgumentError, "invocation policy requires scalar YAML keys"
      end
      if key.value == "<<" || seen.key?(key.value)
        raise ArgumentError, "invocation policy has duplicate or merged YAML keys"
      end
      seen[key.value] = true
    end
  end
  Array(node.children).each { |child| reject_duplicate_keys(child) }
end

begin
  raise ArgumentError, "expected one agents/openai.yaml path" unless ARGV.length == 1

  text = File.read(ARGV.fetch(0), encoding: "UTF-8")
  stream = YAML.parse_stream(text)
  unless stream.children.length == 1
    raise ArgumentError, "invocation policy requires one YAML document"
  end
  reject_duplicate_keys(stream)
  data = YAML.safe_load(text, aliases: false)
  policy = data.is_a?(Hash) ? data["policy"] : nil
  value = policy.is_a?(Hash) ? policy["allow_implicit_invocation"] : nil
  unless value.equal?(true) || value.equal?(false)
    raise ArgumentError, "policy.allow_implicit_invocation must be a boolean"
  end
  puts JSON.generate(value)
rescue Psych::Exception, ArgumentError, SystemCallError => error
  warn "invalid invocation policy: #{error.message.lines.first.strip}"
  exit 1
end
