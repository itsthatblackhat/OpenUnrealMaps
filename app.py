from flask import Flask, render_template, request, jsonify
import os
from PIL import Image
import numpy as np
from osgeo import gdal, ogr, osr

app = Flask(__name__)

# Define directories and paths
DEM_FILE_PATH = 'C:/ProgrammingProjects/OpenUnrealMaps/data/etopo1/ETOPO1_Ice_g_geotiff.tif'  # Path to your local DEM file
OUTPUT_DIR = 'C:/ProgrammingProjects/OpenUnrealMaps/output'
os.makedirs(OUTPUT_DIR, exist_ok=True)

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/create-heightmap', methods=['POST'])
def create_heightmap():
    try:
        data = request.get_json()
        bbox = data.get('bbox')
        if not bbox:
            return jsonify({'error': 'No bounding box provided'}), 400

        # Check if DEM file exists
        if not os.path.isfile(DEM_FILE_PATH):
            return jsonify({'error': 'DEM file not found. Please check the file path.'}), 500

        # Open the DEM file
        src_ds = gdal.Open(DEM_FILE_PATH)
        if src_ds is None:
            raise ValueError('Cannot open DEM file.')

        # Set bounding box coordinates and generate heightmap
        heightmap_path = os.path.join(OUTPUT_DIR, 'heightmap.png')
        generate_heightmap(src_ds, bbox, heightmap_path)

        return jsonify({'message': 'Heightmap created successfully', 'file': heightmap_path})

    except Exception as e:
        return jsonify({'error': f'Unexpected error: {str(e)}'}), 500

def generate_heightmap(src_ds, bbox, output_path):
    # Get geotransform and calculate pixel offsets
    gt = src_ds.GetGeoTransform()
    min_x = int((bbox['west'] - gt[0]) / gt[1])
    max_x = int((bbox['east'] - gt[0]) / gt[1])
    min_y = int((bbox['north'] - gt[3]) / gt[5])
    max_y = int((bbox['south'] - gt[3]) / gt[5])

    # Read the data from the DEM file for the specified bounding box
    data = src_ds.ReadAsArray(min_x, min_y, max_x - min_x, max_y - min_y)
    if data is None:
        raise ValueError('Error reading data from DEM file.')

    # Normalize the data to 0-255 range
    normalized_data = np.clip((data - np.min(data)) / (np.max(data) - np.min(data)) * 255, 0, 255).astype(np.uint8)

    # Save the heightmap as an image
    heightmap_image = Image.fromarray(normalized_data, mode='L')
    heightmap_image.save(output_path)

@app.route('/export-dtm', methods=['POST'])
def export_dtm():
    try:
        data = request.get_json()
        bbox = data.get('bbox')
        if not bbox:
            return jsonify({'error': 'No bounding box provided'}), 400

        # Check if DEM file exists
        if not os.path.isfile(DEM_FILE_PATH):
            return jsonify({'error': 'DEM file not found. Please check the file path.'}), 500

        # Open the DEM file
        src_ds = gdal.Open(DEM_FILE_PATH)
        if src_ds is None:
            raise ValueError('Cannot open DEM file.')

        # Set bounding box coordinates and generate DTM
        dtm_path = os.path.join(OUTPUT_DIR, 'dtm.tif')
        export_dtm_raster(src_ds, bbox, dtm_path)

        return jsonify({'message': 'DTM exported successfully', 'file': dtm_path})

    except Exception as e:
        return jsonify({'error': f'Unexpected error: {str(e)}'}), 500

def export_dtm_raster(src_ds, bbox, output_path):
    # Get geotransform and calculate pixel offsets
    gt = src_ds.GetGeoTransform()
    min_x = int((bbox['west'] - gt[0]) / gt[1])
    max_x = int((bbox['east'] - gt[0]) / gt[1])
    min_y = int((bbox['north'] - gt[3]) / gt[5])
    max_y = int((bbox['south'] - gt[3]) / gt[5])

    # Create a new raster for the specified bounding box
    driver = gdal.GetDriverByName("GTiff")
    out_raster = driver.Create(output_path, max_x - min_x, max_y - min_y, 1, gdal.GDT_Float32)
    out_raster.SetGeoTransform((bbox['west'], gt[1], 0, bbox['north'], 0, gt[5]))
    out_band = out_raster.GetRasterBand(1)

    # Read the data from the DEM file for the specified bounding box
    data = src_ds.ReadAsArray(min_x, min_y, max_x - min_x, max_y - min_y)
    if data is None:
        raise ValueError('Error reading data from DEM file.')

    # Write data to the output raster and set spatial reference
    out_band.WriteArray(data)
    out_band.FlushCache()
    srs = osr.SpatialReference()
    srs.ImportFromEPSG(4326)
    out_raster.SetProjection(srs.ExportToWkt())

    out_band = None
    out_raster = None

@app.route('/export-dtm-png', methods=['POST'])
def export_dtm_png():
    try:
        data = request.get_json()
        bbox = data.get('bbox')
        if not bbox:
            return jsonify({'error': 'No bounding box provided'}), 400

        # Check if DEM file exists
        if not os.path.isfile(DEM_FILE_PATH):
            return jsonify({'error': 'DEM file not found. Please check the file path.'}), 500

        # Open the DEM file
        src_ds = gdal.Open(DEM_FILE_PATH)
        if src_ds is None:
            raise ValueError('Cannot open DEM file.')

        # Set bounding box coordinates and generate DTM PNG
        dtm_png_path = os.path.join(OUTPUT_DIR, 'dtm.png')
        generate_dtm_png(src_ds, bbox, dtm_png_path)

        return jsonify({'message': 'DTM PNG exported successfully', 'file': dtm_png_path})

    except Exception as e:
        return jsonify({'error': f'Unexpected error: {str(e)}'}), 500

def generate_dtm_png(src_ds, bbox, output_path):
    # Get geotransform and calculate pixel offsets
    gt = src_ds.GetGeoTransform()
    min_x = int((bbox['west'] - gt[0]) / gt[1])
    max_x = int((bbox['east'] - gt[0]) / gt[1])
    min_y = int((bbox['north'] - gt[3]) / gt[5])
    max_y = int((bbox['south'] - gt[3]) / gt[5])

    # Read the data from the DEM file for the specified bounding box
    data = src_ds.ReadAsArray(min_x, min_y, max_x - min_x, max_y - min_y)
    if data is None:
        raise ValueError('Error reading data from DEM file.')

    # Normalize the data to 0-255 range
    normalized_data = np.clip((data - np.min(data)) / (np.max(data) - np.min(data)) * 255, 0, 255).astype(np.uint8)

    # Save the DTM as a PNG image
    dtm_image = Image.fromarray(normalized_data, mode='L')
    dtm_image.save(output_path)

@app.route('/create-shapefile', methods=['POST'])
def create_shapefile():
    try:
        data = request.get_json()
        bbox = data.get('bbox')
        if not bbox:
            return jsonify({'error': 'No bounding box provided'}), 400

        shapefile_path = os.path.join(OUTPUT_DIR, 'contours.shp')
        generate_shapefile(bbox, shapefile_path)
        return jsonify({'message': 'Shapefile created successfully', 'file': shapefile_path})

    except Exception as e:
        return jsonify({'error': f'Unexpected error: {str(e)}'}), 500

def generate_shapefile(bbox, shapefile_path):
    dem_path = DEM_FILE_PATH  # Use the DEM file for contour generation

    src_ds = gdal.Open(dem_path)
    if src_ds is None:
        raise ValueError('Cannot open DEM file.')

    driver = ogr.GetDriverByName("ESRI Shapefile")
    if os.path.exists(shapefile_path):
        driver.DeleteDataSource(shapefile_path)

    dst_ds = driver.CreateDataSource(shapefile_path)
    spatial_ref = osr.SpatialReference()
    spatial_ref.ImportFromEPSG(4326)
    dst_layer = dst_ds.CreateLayer("contour", geom_type=ogr.wkbLineString, srs=spatial_ref)
    field_defn = ogr.FieldDefn("ELEV", ogr.OFTReal)
    dst_layer.CreateField(field_defn)

    gdal.ContourGenerate(src_ds.GetRasterBand(1), 0, 0, [10], 0, 0, dst_layer, 0, 0)
    src_ds = None
    dst_ds = None

if __name__ == '__main__':
    app.run(debug=True, port=3000)
