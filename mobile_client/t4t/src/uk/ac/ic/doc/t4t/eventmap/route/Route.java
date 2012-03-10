package uk.ac.ic.doc.t4t.eventmap.route;

public class Route {
	public String name;
	public String description;
	public int color;
	public int width;
	public double[][] route = new double[][] {};
	public RoutePoint[] points = new RoutePoint[] {};
	
	
	public String getName() {
		return name;
	}
	public void setName(String name) {
		this.name = name;
	}
	public String getDescription() {
		return description;
	}
	public void setDescription(String description) {
		this.description = description;
	}
	public int getColor() {
		return color;
	}
	public void setColor(int color) {
		this.color = color;
	}
	public int getWidth() {
		return width;
	}
	public void setWidth(int width) {
		this.width = width;
	}
	public double[][] getRoute() {
		return route;
	}
	public void setRoute(double[][] route) {
		this.route = route;
	}
	public RoutePoint[] getPoints() {
		return points;
	}
	public void setPoints(RoutePoint[] points) {
		this.points = points;
	}
	
	
}
