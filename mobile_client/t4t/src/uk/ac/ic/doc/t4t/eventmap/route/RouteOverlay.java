package uk.ac.ic.doc.t4t.eventmap.route;

import java.util.ArrayList;

import android.graphics.Canvas;
import android.graphics.Color;
import android.graphics.Paint;
import android.graphics.Point;

import com.google.android.maps.GeoPoint;
import com.google.android.maps.MapView;

public class RouteOverlay extends com.google.android.maps.Overlay {
    Route mRoad;
    ArrayList<GeoPoint> mPoints;

    public RouteOverlay(Route road, MapView mv) {
        mRoad = road;
        if (road.route.length > 0) {
            mPoints = new ArrayList<GeoPoint>();
            for (int i = 0; i < road.route.length; i++) {
                mPoints.add(new GeoPoint((int) (road.route[i][1] * 1000000),
                (int) (road.route[i][0] * 1000000)));
            }

        }
    }

    @Override
    public boolean draw(Canvas canvas, MapView mv, boolean shadow, long when) {
        super.draw(canvas, mv, shadow);
        drawPath(mv, canvas);
        return true;
    }

    public void drawPath(MapView mv, Canvas canvas) {
        int x1 = -1, y1 = -1, x2 = -1, y2 = -1;
        Paint paint = new Paint();
        paint.setColor(Color.BLUE);
        paint.setStyle(Paint.Style.STROKE);
        paint.setStrokeWidth(4);
        for (int i = 0; i < mPoints.size(); i++) {
            Point point = new Point();
            mv.getProjection().toPixels(mPoints.get(i), point);
            x2 = point.x;
            y2 = point.y;
            if (i > 0) {
                    canvas.drawLine(x1, y1, x2, y2, paint);
            }
            x1 = x2;
            y1 = y2;
        }
    }
}	