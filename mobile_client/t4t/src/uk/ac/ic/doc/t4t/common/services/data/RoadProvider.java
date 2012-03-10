package uk.ac.ic.doc.t4t.common.services.data;

import java.io.IOException;
import java.io.InputStream;
import java.util.Stack;

import javax.xml.parsers.ParserConfigurationException;
import javax.xml.parsers.SAXParser;
import javax.xml.parsers.SAXParserFactory;

import org.xml.sax.Attributes;
import org.xml.sax.SAXException;
import org.xml.sax.helpers.DefaultHandler;

import uk.ac.ic.doc.t4t.eventmap.route.Route;
import uk.ac.ic.doc.t4t.eventmap.route.RoutePoint;

public class RoadProvider {

	public static Route getRoute(InputStream is) {
		KMLHandler handler = new KMLHandler();
		try {
			SAXParser parser = SAXParserFactory.newInstance().newSAXParser();
			parser.parse(is, handler);
		} catch (ParserConfigurationException e) {
			e.printStackTrace();
		} catch (SAXException e) {
			e.printStackTrace();
		} catch (IOException e) {
			e.printStackTrace();
		}
		return handler.mRoad;
	}

	public static String getUrl(double fromLat, double fromLon, double toLat,
			double toLon) {// connect to map web service
		StringBuffer urlString = new StringBuffer();
		urlString.append("http://maps.google.com/maps?f=d&hl=en");
		urlString.append("&saddr=");// from
		urlString.append(Double.toString(fromLat));
		urlString.append(",");
		urlString.append(Double.toString(fromLon));
		urlString.append("&daddr=");// to
		urlString.append(Double.toString(toLat));
		urlString.append(",");
		urlString.append(Double.toString(toLon));
		urlString.append("&ie=UTF8&0&om=0&output=kml");
		return urlString.toString();
	}
}

class KMLHandler extends DefaultHandler {
	Route mRoad;
	boolean isPlacemark;
	boolean isRoute;
	boolean isItemIcon;
	private Stack mCurrentElement = new Stack();
	private String mString;

	public KMLHandler() {
		mRoad = new Route();
	}

	public void startElement(String uri, String localName, String name,
			Attributes attributes) throws SAXException {
		mCurrentElement.push(localName);
		if (localName.equalsIgnoreCase("Placemark")) {
			isPlacemark = true;
			mRoad.points = addPoint(mRoad.points);
		} else if (localName.equalsIgnoreCase("ItemIcon")) {
			if (isPlacemark)
				isItemIcon = true;
		}
		mString = new String();
	}

	public void characters(char[] ch, int start, int length)
			throws SAXException {
		String chars = new String(ch, start, length).trim();
		mString = mString.concat(chars);
	}

	public void endElement(String uri, String localName, String name)
			throws SAXException {
		if (mString.length() > 0) {
			if (localName.equalsIgnoreCase("name")) {
				if (isPlacemark) {
					isRoute = mString.equalsIgnoreCase("Route");
					if (!isRoute) {
						mRoad.points[mRoad.points.length - 1].name = mString;
					}
				} else {
					mRoad.name = mString;
				}
			} else if (localName.equalsIgnoreCase("color") && !isPlacemark) {
				mRoad.color = Integer.parseInt(mString, 16);
			} else if (localName.equalsIgnoreCase("width") && !isPlacemark) {
				mRoad.width = Integer.parseInt(mString);
			} else if (localName.equalsIgnoreCase("description")) {
				if (isPlacemark) {
					String description = cleanup(mString);
					if (!isRoute)
						mRoad.points[mRoad.points.length - 1].description = description;
					else
						mRoad.description = description;
				}
			} else if (localName.equalsIgnoreCase("href")) {
				if (isItemIcon) {
					mRoad.points[mRoad.points.length - 1].iconUrl = mString;
				}
			} else if (localName.equalsIgnoreCase("coordinates")) {
				if (isPlacemark) {
					if (!isRoute) {
						String[] xyParsed = split(mString, ",");
						double lon = Double.parseDouble(xyParsed[0]);
						double lat = Double.parseDouble(xyParsed[1]);
						mRoad.points[mRoad.points.length - 1].latitude = lat;
						mRoad.points[mRoad.points.length - 1].longitude = lon;
					} else {
						String[] coodrinatesParsed = split(mString, " ");
						int lenNew = coodrinatesParsed.length;
						int lenOld = mRoad.route.length;
						double[][] temp = new double[lenOld + lenNew][2];
						for (int i = 0; i < lenOld; i++) {
							temp[i] = mRoad.route[i];
						}
						for (int i = 0; i < lenNew; i++) {
							String[] xyParsed = split(coodrinatesParsed[i], ",");
							for (int j = 0; j < 2 && j < xyParsed.length; j++)
								temp[lenOld + i][j] = Double
										.parseDouble(xyParsed[j]);
						}
						mRoad.route = temp;						
					}
				}
			}
		}
		mCurrentElement.pop();
		if (localName.equalsIgnoreCase("Placemark")) {
			isPlacemark = false;
			if (isRoute)
				isRoute = false;
		} else if (localName.equalsIgnoreCase("ItemIcon")) {
			if (isItemIcon)
				isItemIcon = false;
		}
	}

	private String cleanup(String value) {
		String remove = "<br/>";
		int index = value.indexOf(remove);
		if (index != -1)
			value = value.substring(0, index);
		remove = "&#160;";
		index = value.indexOf(remove);
		int len = remove.length();
		while (index != -1) {
			value = value.substring(0, index).concat(
					value.substring(index + len, value.length()));
			index = value.indexOf(remove);
		}
		return value;
	}

	public RoutePoint[] addPoint(RoutePoint[] points) {
		RoutePoint[] result = new RoutePoint[points.length + 1];
		for (int i = 0; i < points.length; i++)
			result[i] = points[i];
		result[points.length] = new RoutePoint();
		return result;
	}

	private static String[] split(String strString, String strDelimiter) {
		String[] strArray;
		int iOccurrences = 0;
		int iIndexOfInnerString = 0;
		int iIndexOfDelimiter = 0;
		int iCounter = 0;
		if (strString == null) {
			throw new IllegalArgumentException("Input string cannot be null.");
		}
		if (strDelimiter.length() <= 0 || strDelimiter == null) {
			throw new IllegalArgumentException(
					"Delimeter cannot be null or empty.");
		}
		if (strString.startsWith(strDelimiter)) {
			strString = strString.substring(strDelimiter.length());
		}
		if (!strString.endsWith(strDelimiter)) {
			strString += strDelimiter;
		}
		while ((iIndexOfDelimiter = strString.indexOf(strDelimiter,
				iIndexOfInnerString)) != -1) {
			iOccurrences += 1;
			iIndexOfInnerString = iIndexOfDelimiter + strDelimiter.length();
		}
		strArray = new String[iOccurrences];
		iIndexOfInnerString = 0;
		iIndexOfDelimiter = 0;
		while ((iIndexOfDelimiter = strString.indexOf(strDelimiter,
				iIndexOfInnerString)) != -1) {
			strArray[iCounter] = strString.substring(iIndexOfInnerString,
					iIndexOfDelimiter);
			iIndexOfInnerString = iIndexOfDelimiter + strDelimiter.length();
			iCounter += 1;
		}

		return strArray;
	}
}