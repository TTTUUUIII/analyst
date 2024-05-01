(function () {
    Analyst = {
        plot_contour: function (desc) {

            let data = desc["data"], row = desc["row"], col = desc["col"]
            let datasheet = []
            for (i = 0; i < row; ++i) {
                let g = []
                for (j = i * row; j < i * row + row; ++j) {
                    g.push(data[j])
                }
                datasheet.push(g)
            }
            var option = [{
                z: datasheet,
                type: "contour",
                colorscale: desc["style"]["colorscale"],
                transpose: desc["transpose"] ?? false,
                contours: {
                    coloring: desc["style"]["coloring"],
                    showlabels: desc["style"]["showlables"],
                    labelfont: {
                        size: desc["style"]["labelsize"],
                        color: desc["style"]["labelcolor"],
                        family: desc["style"]["fontfamily"]
                    },
                },
                line: {
                    width: desc["style"]["linewidth"],
                    color: desc["style"]["linecolor"],
                    smoothing: desc["style"]["linesmoothing"]
                },
                colorbar: {
                    tickfont: {
                        size: desc["style"]["barsize"],
                        color: desc["style"]["barcolor"],
                        family: desc["style"]["fontfamily"]
                    },
                    thickness: desc["style"]["barwidth"]
                }
            }
            ];

            var layout = {
                title: {
                    text: desc["title"] ?? "",
                    font: {
                        size: desc["style"]["titlesize"],
                        color: desc["style"]["titlecolor"],
                        family: desc["style"]["fontfamily"]
                    }
                },
                font: {
                    size: desc["style"]["fontsize"],
                    family: desc["style"]["fontfamily"],
                    color: desc["style"]["fontcolor"]
                },
                paper_bgcolor: desc["style"]["paperbgcolor"],
                plot_bgcolor: desc["style"]["plotbgcolor"]
            }
            Plotly.newPlot(container, option, layout);
        }
    }
})()