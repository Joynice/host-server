/**
 * @author Alex Andrix <alex@alexandrix.com>
 * @since 2018-12-22
 */

var App = {};
App.setup = function() {
  var canvas = document.createElement('canvas');
  this.filename = "twopointfive";
  canvas.width = window.innerWidth;
  canvas.height = window.innerHeight;
  this.canvas = canvas;
  document.getElementsByTagName('body')[0].appendChild(canvas);
  this.ctx = this.canvas.getContext('2d');
  this.width = this.canvas.width;
  this.height = this.canvas.height;
  this.dataToImageRatio = 1;
  this.ctx.imageSmoothingEnabled = false;
  this.ctx.webkitImageSmoothingEnabled = false;
  this.ctx.msImageSmoothingEnabled = false;
  this.xC = this.width / 2;
  this.yC = this.height / 2;

  this.stepCount = 0;
  this.particles = [];
  this.lifespan = 800;
  this.popPerBirth = 3;
  this.maxPop = 300;
  this.birthFreq = 1;

  // Build grid of attractors (simple triangle here)
  this.grid = [];
  var i = 0;
  this.triangleRad = 250;
  var r = this.triangleRad;
  this.grid.push({x: -r * Math.sqrt(3)/2, y: 0, spotIndex: 1});
  this.grid.push({x: r, y: -r, spotIndex: 2});
  this.grid.push({x: r, y: r, spotIndex: 3});
  this.gridMaxIndex = 3;

  // Counters for UI
  this.drawnInLastFrame = 0;
  this.deathCount = 0;

  this.initDraw();
};
App.evolve = function() {
  var time1 = performance.now();

  this.stepCount++;

  // Rotate grid (triangle)
  var angle = this.stepCount / 800,
      r = this.triangleRad;
  this.grid[0].x = r * Math.cos(angle);
  this.grid[0].y = r * Math.sin(angle);
  angle += 2 * Math.PI / 3;
  this.grid[1].x = r * Math.cos(angle);
  this.grid[1].y = r * Math.sin(angle);
  angle += 2 * Math.PI / 3;
  this.grid[2].x = r * Math.cos(angle);
  this.grid[2].y = r * Math.sin(angle);

  if (this.stepCount % this.birthFreq == 0 && (this.particles.length + this.popPerBirth) < this.maxPop) {
    this.birth();
  }
  App.move();
  App.draw();

  var time2 = performance.now();

  // Update UI
  document.getElementsByClassName('dead')[0].textContent = this.deathCount;
  document.getElementsByClassName('alive')[0].textContent = this.particles.length;
  document.getElementsByClassName('fps')[0].textContent = Math.floor(1000 / (time2 - time1));
  document.getElementsByClassName('drawn')[0].textContent = this.drawnInLastFrame;

};
App.birth = function() {
  var x, y;
  var gridSpotIndex = Math.floor(Math.random() * this.gridMaxIndex),
      gridSpot = this.grid[gridSpotIndex],
      //x = gridSpot.x, y = gridSpot.y;
      x = 300 * (2 * Math.random() - 1), y = 300 * (2 * Math.random() - 1);

  var particle = {
    hue: 230,// + Math.floor(50*Math.random()),
    sat: 100,//30 + Math.floor(70*Math.random()),
    lum: 30 + Math.floor(20*Math.random()),
    x: x, y: y,
    xLast: x, yLast: y,
    xSpeed: 0, ySpeed: 0,
    age: 0,
    attractorIndex: gridSpotIndex,
    name: 'seed-' + Math.ceil(10000000 * Math.random())
  };
  this.particles.push(particle);
};
App.kill = function(particleName) {
 var newArray = _.reject(this.particles, function(seed) {
    return (seed.name == particleName);
  });
  this.particles = _.cloneDeep(newArray);
};
App.move = function() {
  for (var i = 0; i < this.particles.length; i++) {
    // Get particle
    var p = this.particles[i];

    // Save last position
    p.xLast = p.x; p.yLast = p.y;

    // Attractor and corresponding grid spot
    var index = p.attractorIndex,
        gridSpot = this.grid[index];

    // Maybe move attractor
    var prob = 0.55 * Math.abs(Math.sin(this.stepCount/40));
    prob = Math.pow(prob, 3);
    if (Math.random() < prob) {
      // Move attractor
      p.attractorIndex = Math.floor(Math.random() * this.gridMaxIndex);
    }

    // Spring attractor to center with viscosity
    var k = 0.8, visc = 0.4;
    var dx = p.x - gridSpot.x,
        dy = p.y - gridSpot.y,
        dist = Math.sqrt(dx*dx + dy*dy);

    // Spring
    var xAcc = -k * dx,
        yAcc = -k * dy;

    p.xSpeed += xAcc; p.ySpeed += yAcc;

    // Calm the f*ck down
    p.xSpeed *= visc; p.ySpeed *= visc;

    // Store stuff in particle brain
    p.speed = Math.sqrt(p.xSpeed * p.xSpeed + p.ySpeed * p.ySpeed);
    p.dist = dist;

    // Update position
    p.x += 0.1 * p.xSpeed; p.y += 0.1 * p.ySpeed;

    // Get older
    p.age++;

    // Kill if too old
    if (p.age > this.lifespan) {
      this.kill(p.name);
      this.deathCount++;
    }
  }
};
App.initDraw = function() {
  this.ctx.beginPath();
  this.ctx.rect(0, 0, this.width, this.height);
  this.ctx.fillStyle = 'black';
  this.ctx.fill();
  this.ctx.closePath();
};
App.draw = function() {
  this.drawnInLastFrame = 0;
  if (!this.particles.length) return false;

  this.ctx.beginPath();
  this.ctx.rect(0, 0, this.width, this.height);
  this.ctx.fillStyle = 'rgba(0, 0, 0, 0.1)';
  //this.ctx.fillStyle = 'rgba(255, 255, 255, 0.1)';
  this.ctx.fill();
  this.ctx.closePath();

  for (var i = 0; i < this.particles.length; i++) {
    // Draw particle
    var p = this.particles[i];

    var h, s, l, a;

    h = p.hue;// + this.stepCount/30;
    s = p.sat;
    l = p.lum;
    a = 1;

    var last = this.dataXYtoCanvasXY(p.xLast, p.yLast),
        now = this.dataXYtoCanvasXY(p.x, p.y);
    var attracSpot = this.grid[p.attractorIndex],
        attracXY = this.dataXYtoCanvasXY(attracSpot.x, attracSpot.y);
    this.ctx.beginPath();

    this.ctx.strokeStyle = 'hsla(' + h + ', ' + s + '%, ' + l + '%, ' + a + ')';
    this.ctx.fillStyle = 'hsla(' + h + ', ' + s + '%, ' + l + '%, ' + a + ')';

    // Particle trail
    this.ctx.moveTo(last.x, last.y);
    this.ctx.lineTo(now.x, now.y);
    var rDrawn = Math.max(0.3, 2 - Math.sqrt(p.x*p.x + p.y * p.y) / 50);
    this.ctx.lineWidth = 1.5 * rDrawn * this.dataToImageRatio;
    this.ctx.stroke();
    this.ctx.closePath();

    // Attractor positions
    /*
    this.ctx.beginPath();
    this.ctx.lineWidth = 1.5 * this.dataToImageRatio;
    this.ctx.arc(attracXY.x, attracXY.y, 1.5 * this.dataToImageRatio, 0, 2 * Math.PI, false);

    a /= 20;
    this.ctx.strokeStyle = 'hsla(' + h + ', ' + s + '%, ' + l + '%, ' + a + ')';
    this.ctx.fillStyle = 'hsla(' + h + ', ' + s + '%, ' + l + '%, ' + a + ')';
    this.ctx.stroke();
    this.ctx.fill();
    */

    this.ctx.closePath();

    // UI counter
    this.drawnInLastFrame++;
  }

};
App.dataXYtoCanvasXY = function(x, y) {
  var zoom = 1.1;
  var xx = this.xC + x * zoom * this.dataToImageRatio,
      yy = this.yC + y * zoom * this.dataToImageRatio;

  return {x: xx, y: yy};
};

document.addEventListener('DOMContentLoaded', function() {
  App.setup();
  App.draw();

  var frame = function() {
    App.evolve();
    requestAnimationFrame(frame);
  };
  frame();
});


/**
 * Some old util I use at times
 *
 * @param {Number} Xstart X value of the segment starting point
 * @param {Number} Ystart Y value of the segment starting point
 * @param {Number} Xtarget X value of the segment target point
 * @param {Number} Ytarget Y value of the segment target point
 * @param {Boolean} realOrWeb true if Real (Y towards top), false if Web (Y towards bottom)
 * @returns {Number} Angle between 0 and 2PI
 */
segmentAngleRad = function(Xstart, Ystart, Xtarget, Ytarget, realOrWeb) {
	var result;// Will range between 0 and 2PI
	if (Xstart == Xtarget) {
		if (Ystart == Ytarget) {
			result = 0;
		} else if (Ystart < Ytarget) {
			result = Math.PI/2;
		} else if (Ystart > Ytarget) {
			result = 3*Math.PI/2;
		} else {}
	} else if (Xstart < Xtarget) {
		result = Math.atan((Ytarget - Ystart)/(Xtarget - Xstart));
	} else if (Xstart > Xtarget) {
		result = Math.PI + Math.atan((Ytarget - Ystart)/(Xtarget - Xstart));
	}

	result = (result + 2*Math.PI)%(2*Math.PI);

	if (!realOrWeb) {
		result = 2*Math.PI - result;
	}

	return result;
};

$(function () {
  $(".readerme").click(function (event) {
    event.preventDefault();
    var dialog = $("#readerme-dialog");
    var readerme = "<ul class=\"list-group\">\n" +
        "  <li class=\"list-group-item\">1. title=\"abc\" 从标题中搜索包含abc。</li>\n" +
        "  <li class=\"list-group-item\">2. server=\"abc\"搜索使用abc服务器的网站信息。</li>\n" +
        "  <li class=\"list-group-item\">3. os=\"abc\"使用abc操作系统的网站信息。</li>\n" +
        "  <li class=\"list-group-item\">4. ip=\"abc\"指定IP的网站信息。</li>\n" +
        "</ul>";
    $("#readerme-body").html(readerme);
    dialog.modal('show')
  })
});

function setHeightKeyWord(keyword) {
    /* 获取需要处理的关键字 */
    var tempHTML = $("#result-dialog").html();
    /* 关键字替换文本 该文本设置有高亮颜色 */
    var replaceText = "<font style='color:red;'>$1</font>";
    /* 关键字正则匹配规则 */
    var r = new RegExp("(" + keyword + ")", "ig");
    /* 将匹配到的关键字替换成我们预设的文本 */
    tempHTML = tempHTML.replace(r, replaceText);
    /* 将文本显示到浏览器上 */
    $("#result-dialog").html(tempHTML);
}

$(function () {
  $("#search").click(function (event) {
    event.preventDefault();
    var searchInput = $("#data");
    var data = searchInput.val();
    var dialog = $("#result-dialog");
    if (data == '') {
      zlalert.alertInfoToast('请输入查询内容!');
      return;
    }
    var reg=new RegExp('.*[\"]+(.*)[\"]+.*');
    var search_data = data.replace(reg,"$1");
    console.log(search_data);
    zlajax.post({
      'url': '/',
      'data': {
        'search': data
      },
      'success': function (data) {
        if (data['code'] == 200) {
          result = data['data'];
          var html = "";
          for (var i=0; i<result.length; i++) {
            zlalert.alertSuccessToast('查询成功!');
            var url = result[i]['url'];
            html += "<ul class='list-group'>";
            html += "<h4>" +"<a href="+url+" target='_blank'>"+ url + "</a>"+ "</h4>";
            html += "<li class='list-group-item'>" + 'IP： ' +result[i]['ip'] + "</li>";
            html += "<li class='list-group-item'>" + '标题： '+ result[i]['title'] + "</li>";
            html += "<li class='list-group-item'>" + 'Web服务器： '+result[i]['web_server'] + "</li>";
            html += "<li class='list-group-item'>" + 'Js框架： '+ result[i]['jsf'] + "</li>";
            html += "<li class='list-group-item'>" + 'Web框架： '+result[i]['wf'] + "</li>";
            html += "<li class='list-group-item'>" + '操作系统： '+result[i]['os'] + "</li>";
            html += "<li class='list-group-item'>" + 'CMS： '+result[i]['cms'] + "</li>";
            html += "<li class='list-group-item'>" + '更新时间： ' +result[i]['ut'] + "</li>";
            html += "<li class='list-group-item'>" + '端口信息： '+result[i]['ports'] + "</li>";
            html += "</ul>";
          }
          $("#result-body").html(html);
          dialog.modal('show');
          setHeightKeyWord(search_data);
        } else {
          zlalert.alertInfoToast(data['message']);
        }
      },
      'fail': function () {
        zlalert.alertNetworkError()
      }

    })


  })
});

$(function () {
   $(".jumbotron").mouseenter(function () {
       $(this).css({"filter":"alpha(Opacity=80)","-moz-opacity":0.8,"opacity":0.8})
   })
});
$(function () {
   $(".jumbotron").mouseleave(function () {
        $(this).css({"filter":"alpha(Opacity=30)","-moz-opacity":0.3,"opacity":0.3})
   })
});
