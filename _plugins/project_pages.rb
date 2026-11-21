# Skips generating a project page (_research/, _portfolio/) when it isn't needed:
#
#   `link:` set in front matter -> card opens that URL; no page is generated
#   no body below front matter  -> card is not clickable; no page is generated
#   otherwise                   -> card opens the project's own page
#
# The card target itself is computed in _includes/project_list.html (same rules).
module ProjectPages
  COLLECTIONS = %w(research portfolio).freeze

  def self.own_page?(doc)
    doc.data["link"].to_s.strip.empty? && !doc.content.to_s.strip.empty?
  end
end

Jekyll::Hooks.register :site, :post_read do |site|
  ProjectPages::COLLECTIONS.each do |name|
    coll = site.collections[name] or next
    coll.docs.each do |doc|
      next if ProjectPages.own_page?(doc)
      doc.data["sitemap"] = false
      doc.define_singleton_method(:write?) { false }
    end
  end
end
