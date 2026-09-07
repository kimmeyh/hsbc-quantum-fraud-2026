--[[
float-tables.lua -- make pandoc tables into LaTeX floats (F36, card #48).

STATUS: NOT REGISTERED. This filter works, but the problem it was built for did
not exist, and enabling it by default COSTS a page in a table-dense document
(gate_report.pdf goes 3 -> 4). Read docs/reviews/f36-float-tables-outcome.md
before wiring this into any render. It is opt-in through render-pdf.ps1's
-LuaFilter parameter and nothing passes it today.

The premise below is preserved as it was written, because it is wrong in an
instructive way: the page-fill measurement it rests on counted CHARACTERS, and
a table-heavy page always looks short by that measure. Measured as vertical
extent, every page cited here was already full.

THE PROBLEM THIS SOLVES, measured rather than assumed.

The appendix content FITS three pages and renders on four. Page fills were
2,695 / 3,807 / 2,550 / 1,788 = 10,840 characters, against a three-page capacity
of 11,421 at page 2's density -- 581 characters UNDER, yet needing a fourth page.

pandoc emits pipe tables as bare `longtable` environments. longtable breaks
across pages but never FLOATS: it starts exactly where it is written. When a
table does not fit the space remaining, LaTeX defers the table AND everything
after it, leaving the page short. Five tables of 35 rows left pages 1 and 3
roughly 1,100 characters below page 2.

A dry run confirmed the diagnosis before this filter was written: rendering the
appendix with all five tables removed gives 3 pages, while the tables' own text
is only about 1,400 characters. The gap is break waste, which is what floats
recover.

`ltablex` was tried first and cannot work here: a float must be wrapped in
`\begin{table}` and longtable may not legally sit inside one, so there was
nothing for LaTeX to move.

WHAT THIS FILTER DOES

Each Table node is emitted as a floating `table` environment with `[htbp]`
placement, so LaTeX may set it on the page before or after the prose that
introduces it. Inside the float the table is a plain `tabular`, which a float
can contain. Every table gets a caption and a label, because a float that has
moved needs a name the prose can reference.

WHY tabular RATHER THAN longtable IS SAFE HERE

Our tables are 6 to 9 rows. None approaches a page, so none needs longtable's
page-breaking. A table that genuinely needed to break would be a reason NOT to
float it, and the filter leaves any table above MAX_FLOAT_ROWS alone rather than
producing a float that overflows its page.

A table that already carries a caption is left untouched: the author asked for
something specific and this filter should not second-guess it.
]]

local MAX_FLOAT_ROWS = 25   -- above this, keep longtable's page-breaking

-- Count body rows so an oversized table is left as a longtable.
local function body_rows(tbl)
  local n = 0
  for _, body in ipairs(tbl.bodies or {}) do
    n = n + #(body.body or {})
  end
  return n
end

local function has_caption(tbl)
  local c = tbl.caption
  return c and c.long and #c.long > 0
end

local counter = 0

-- Emitting each table as a RawBlock bypasses pandoc's package detection: it
-- no longer sees a Table node, so it does not load booktabs or array itself.
-- Inject exactly the packages the rewritten float needs.
function Meta(meta)
  local hi = meta["header-includes"]
  if hi == nil then
    hi = pandoc.MetaList({})
  elseif hi.t ~= "MetaList" then
    hi = pandoc.MetaList({ hi })
  end
  hi[#hi + 1] = pandoc.MetaBlocks({
    pandoc.RawBlock("latex", "\\usepackage{booktabs}"),
    pandoc.RawBlock("latex", "\\usepackage{array}"),
    -- pandoc's column widths use \real{}, which comes from its own calc
    -- preamble -- emitted only when it SEES a Table node. Our RawBlock
    -- hides them, so calc must be loaded explicitly or every width is
    -- "Missing number, treated as zero".
    pandoc.RawBlock("latex", "\\usepackage{calc}"),
    pandoc.RawBlock("latex", "\\usepackage{etoolbox}"),
  })
  meta["header-includes"] = hi
  return meta
end

-- Convert one longtable body into a tabular suitable for a float.
--
-- longtable emits its head/foot machinery BEFORE the body:
--
--     <first head>  \endfirsthead      (only when a repeated head differs)
--     <repeat head> \endhead
--     \bottomrule   \endlastfoot
--     <body rows>
--     \end{longtable}
--
-- Two earlier attempts were wrong, and both faults were visible in the
-- rendered PDF. Deleting only the MARKERS left the repeated head as a
-- duplicate header row and left \bottomrule sitting ABOVE the body. Deleting
-- from \endfirsthead missed every table pandoc gives a single head, because
-- those have no \endfirsthead at all -- their machinery still shipped into
-- the tabular.
--
-- So: delete from the FIRST head marker present through \endlastfoot, keep
-- the head above it, and re-add the bottom rule after the body.
local function longtable_to_tabular(latex)
  -- \endhead is always present; \endfirsthead only sometimes. Anchoring on
  -- \endhead therefore covers both shapes, and the ".-" stops at the first
  -- \endlastfoot so a second table in the same string is untouched.
  latex = latex:gsub("\\endfirsthead", "\\endhead")
  latex = latex:gsub("\\endhead.-\\endlastfoot", "")
  -- The repeated-head block sat between the two markers and is now gone; any
  -- \endhead left behind belonged to a head we keep.
  latex = latex:gsub("\\endhead%s*", "")

  latex = latex:gsub("\\begin{longtable}%[%]", "\\begin{tabular}")
  latex = latex:gsub("\\begin{longtable}", "\\begin{tabular}")
  -- The bottom rule went out with the foot block; restore it below the body.
  latex = latex:gsub("\\end{longtable}", "\\bottomrule\\noalign{}\n\\end{tabular}")

  -- A caption inside a tabular is invalid; the float carries it instead.
  latex = latex:gsub("\\caption[^\n]*\\\\", "")
  latex = latex:gsub("\\caption[^\n]*\n", "")
  return latex
end

function Table(tbl)
  -- Leave captioned tables alone: the author made an explicit choice.
  if has_caption(tbl) then
    return nil
  end

  -- Leave long tables as longtable; they need page-breaking more than
  -- floating, and a float that cannot fit its page is worse than an inline
  -- table.
  if body_rows(tbl) > MAX_FLOAT_ROWS then
    return nil
  end

  counter = counter + 1
  local label = "tbl:auto" .. counter

  -- Render the table as pandoc would, then rewrite it into a float. The
  -- caption is deliberately EMPTY: these tables are introduced by the prose
  -- around them, and inventing descriptive captions here would put words in
  -- the author's mouth. \caption{} still numbers the float, which is what
  -- \label and \ref need in order to resolve.
  local latex = pandoc.write(pandoc.Pandoc({ tbl }), "latex")
  latex = longtable_to_tabular(latex)

  local float = table.concat({
    "\\begin{table}[htbp]",
    "\\centering",
    latex,
    "\\caption{}",
    "\\label{" .. label .. "}",
    "\\end{table}",
  }, "\n")

  return pandoc.RawBlock("latex", float)
end
