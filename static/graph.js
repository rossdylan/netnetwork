var width = window.width || 1060;
var height = window.height || 600;

var svg = d3.select("body").append("svg")
    .attr("width", width)
    .attr("height", height);

var force = d3.layout.force()
    .gravity(0.5)
    .distance(200)
    .charge(-2000)
    .size([width, height])
    .nodes([])
    .links([])
    .start();


var node = svg.selectAll(".node");
var link = svg.selectAll("line");
var connection = new WebSocket('ws://localhost:8080/ws', []);
connection.onmessage = function(event) {
        var jsonData = JSON.parse(event.data);
        console.log(jsonData);
        //node = node.data(jsonData.nodes, function(d) { return d.name; });
        //link = link.data(jsonData.links, function(d) { return d.source + "-" + d.target; });
        node = node.data(jsonData.nodes);
        link = link.data(jsonData.links);
        link.exit().remove();
        link.enter().append("line")
            .attr("class", "link");
        node.exit().remove();
        var nodeEnter = node.enter().append("g")
            .attr("class", "node")
            .call(force.drag);
        nodeEnter.append("circle")
            .attr("r", function(d) { return 10.5 });
        nodeEnter.append("text")
              .attr("dx", 12)
              .attr("dy", ".35em")
              .text(function(d) { return d.name; });
        node.select("circle")
            .style("fill", "steelblue");
        force.on("tick", function() {
            link.attr("x1", function(d) { return d.source.x; })
                .attr("y1", function(d) { return d.source.y; })
                .attr("x2", function(d) { return d.target.x; })
                .attr("y2", function(d) { return d.target.y; });
            node.attr("transform", function(d) { return "translate(" + d.x + "," + d.y + ")"; });
        });
        force
            .nodes(jsonData.nodes)
            .links(jsonData.links)
            .start();
};
