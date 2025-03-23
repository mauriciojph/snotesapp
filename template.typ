#import "@preview/ez-today:0.1.0"
#import "@preview/mitex:0.2.5": *
#import "@preview/cmarker:0.1.2"

#let autor = [Mauricio Pérez]
#let lang = "es" // "es", "en", ...

#let project(
  title: "",
  date: none,
  body,
) = {
  // Set the document's basic properties.
  set document(title: title)
  set page(
    numbering: "1",
    number-align: right,
    footer: context {
      if counter(page).get().first() >= 1 [ // make the sign > to not enable headers in the first page
        \[#title - #autor\]
        #h(1fr)
        #counter(page).display()
      ]
    }
  )
  set text(font: "Libertinus Serif", lang: lang)

  //set heading(numbering: "1.1")

  // Set run-in subheadings, starting at level 4.
  show heading: it => {
    if it.level > 3 {
      parbreak()
      text(11pt, style: "italic", weight: "regular", smallcaps(it.body + "."))
    } else {
      smallcaps(it)
    }
  }

  set par(leading: 0.58em)

  // Title row.
  line(length: 100%, stroke: 1.5pt)
  align(center)[
    #block(text(weight: 700, 2em, title))
    #v(1em, weak: true)
  ]
  line(length: 100%, stroke: 1.5pt)
  align(center)[
    #v(0.8em, weak: true)
    // #date #h(6em) Hecho por #autor
    #h(1fr) #date\; #autor #h(1fr)
  ]

  // Main body.
  show: columns.with(2, gutter: 1.5em)
  set par(justify: true)
  set image(fit: "contain", width: 90%)

  body
}

#let my-months = ("Enero", "Febrero", "Marzo", "Abril", "Mayo", "Junio", "Julio", "Agosto", "Septiembre", "Octubre", "Noviembre", "Diciembre") // spanish months

#let content-replace(c, r, v) = {
  for child in c.children {
    if child.text != "" {
      [#child.text.replace(r, v)]
    } else {
      [#child]
    }
  }
}

#show: project.with(
  title: [$title],
  //date: ez-today.today(lang: "es", format: "M d, Y")
  date: content-replace(ez-today.today(custom-months: my-months, format: "d ^ M, Y"), "^", "de")
)

$body
