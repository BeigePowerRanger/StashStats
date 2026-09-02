-- wikilinks.lua
-- Converts internal markdown/qmd links to Obsidian [[wikilinks]], preserves [[...]] syntax,
-- and formats standard Obsidian YAML frontmatter (--- ... ---) at the top of GFM output.

local function format_yaml_value(val)
  local vtype = pandoc.utils.type(val)
  if vtype == "List" then
    local lines = {}
    for _, item in ipairs(val) do
      table.insert(lines, "  - " .. pandoc.utils.stringify(item))
    end
    return lines
  elseif vtype == "boolean" then
    return tostring(val)
  else
    return pandoc.utils.stringify(val)
  end
end

function Link(el)
  local target = el.target
  if not target or target == "" then
    return el
  end

  -- Skip external links
  if target:match("^https?://") or target:match("^mailto:") or target:match("^ftp://") then
    return el
  end

  -- Skip anchor-only links within same page
  if target:match("^#") then
    return el
  end

  -- Separate note path and possible fragment: "client-stash.qmd#section" -> note="client-stash.qmd", fragment="#section"
  local note_path, fragment = target:match("([^#]*)(#?.*)")
  if not note_path or note_path == "" then
    return el
  end

  -- Strip .qmd / .md extension
  local note = note_path:gsub("%.qmd$", ""):gsub("%.md$", "")
  -- Strip directory prefixes if any
  note = note:gsub(".*/", "")

  -- If fragment exists and is not empty, attach it: "client-stash#get_stash"
  if fragment and fragment ~= "" then
    note = note .. fragment
  end

  local text = pandoc.utils.stringify(el.content)

  -- Check if text matches note
  if text == note or text == "" then
    return pandoc.RawInline('markdown', '[[' .. note .. ']]')
  else
    return pandoc.RawInline('markdown', '[[' .. note .. '|' .. text .. ']]')
  end
end

local function process_accumulated_text(text, result)
  local pos = 1
  while true do
    local open_start, open_end = text:find("%[%[", pos)
    if not open_start then
      local remainder = text:sub(pos)
      if remainder ~= "" then
        table.insert(result, pandoc.Str(remainder))
      end
      break
    end
    
    if open_start > pos then
      local prefix = text:sub(pos, open_start - 1)
      table.insert(result, pandoc.Str(prefix))
    end
    
    local close_start, close_end = text:find("%]%]", open_end + 1)
    if not close_start then
      -- Unclosed [[
      local remainder = text:sub(open_start)
      table.insert(result, pandoc.Str(remainder))
      break
    end
    
    local link_content = text:sub(open_end + 1, close_start - 1)
    table.insert(result, pandoc.RawInline('markdown', "[[" .. link_content .. "]]"))
    pos = close_end + 1
  end
end

function Inlines(inlines)
  local result = {}
  local i = 1
  while i <= #inlines do
    local el = inlines[i]
    if el.t == "Str" and el.text:find("%[%[") then
      local accumulated_text = el.text
      local elements_consumed = 1
      while not accumulated_text:find("%]%]") and (i + elements_consumed <= #inlines) do
        local next_el = inlines[i + elements_consumed]
        accumulated_text = accumulated_text .. pandoc.utils.stringify(next_el)
        elements_consumed = elements_consumed + 1
      end
      
      process_accumulated_text(accumulated_text, result)
      i = i + elements_consumed
    else
      table.insert(result, el)
      i = i + 1
    end
  end
  return result
end

function Pandoc(doc)
  -- Filter internal / quarto metadata keys that should not be in user frontmatter
  local ignored_keys = {
    ["biblio-config"] = true,
    ["labels"] = true,
    ["include-before"] = true,
    ["include-after"] = true,
    ["header-includes"] = true,
    ["toc-title"] = true,
    ["document-css"] = true,
    ["link-citations"] = true,
    ["date-format"] = true,
    ["lang"] = true,
    ["crossref"] = true,
    ["standalone"] = true,
    ["template"] = true
  }

  local has_meta = false
  for k, _ in pairs(doc.meta) do
    if not ignored_keys[k] then
      has_meta = true
      break
    end
  end

  if has_meta then
    local yaml_lines = {"---"}
    local ordered_keys = {"title", "created", "updated", "type", "tags", "aliases"}
    local processed = {}

    for _, key in ipairs(ordered_keys) do
      local val = doc.meta[key]
      if val ~= nil then
        processed[key] = true
        local vtype = pandoc.utils.type(val)
        if vtype == "List" then
          table.insert(yaml_lines, key .. ":")
          for _, item in ipairs(val) do
            table.insert(yaml_lines, "  - " .. pandoc.utils.stringify(item))
          end
        else
          table.insert(yaml_lines, key .. ": " .. pandoc.utils.stringify(val))
        end
      end
    end

    -- Process any additional custom keys in doc.meta
    for key, val in pairs(doc.meta) do
      if not processed[key] and not ignored_keys[key] then
        local vtype = pandoc.utils.type(val)
        if vtype == "List" then
          table.insert(yaml_lines, key .. ":")
          for _, item in ipairs(val) do
            table.insert(yaml_lines, "  - " .. pandoc.utils.stringify(item))
          end
        else
          table.insert(yaml_lines, key .. ": " .. pandoc.utils.stringify(val))
        end
      end
    end

    table.insert(yaml_lines, "---")
    table.insert(yaml_lines, "")

    local yaml_block = table.concat(yaml_lines, "\n")
    table.insert(doc.blocks, 1, pandoc.RawBlock('markdown', yaml_block))
  end

  -- Clear title from meta so Pandoc doesn't emit a duplicate H1 header
  doc.meta.title = nil

  return doc
end
