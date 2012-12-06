fonts = [['Sonsie One', 54],
         ['Poiret One', 90],
         ['Freckle Face', 90],
         ['Keania One', 90],
         ['Rye', 78],
         ['Play', 90],
         ['Miss Fajardose', 100],
         ['Yanone Kaffeesatz', 72]
        ];

$(function() {
  var index = Math.floor(Math.random() * fonts.length);

  $('#brand').css('font-family', fonts[index][0]);
  $('#brand').css('font-size', fonts[index][1]);
});

